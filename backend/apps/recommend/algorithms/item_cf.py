import math
from collections import defaultdict

from apps.practice.models import UserQuestionStatus
from apps.recommend.models import QuestionSimilarity
from .base import BaseRecommender


class ItemBasedCF(BaseRecommender):
    """基于物品的协同过滤"""

    def get_name(self):
        return 'item_cf'

    def recommend(self, user, n=5, exclude_ids=None):
        exclude_ids = exclude_ids or set()

        user_scores = dict(
            UserQuestionStatus.objects.filter(user=user)
            .values_list('question_id', 'best_score')
        )
        if not user_scores:
            return []

        user_question_ids = set(user_scores.keys())

        # 获取用户做过的题的相似题
        question_scores = defaultdict(float)
        question_weights = defaultdict(float)

        sim_records = QuestionSimilarity.objects.filter(
            question_a_id__in=user_question_ids, similarity__gt=0
        ).order_by('-similarity')

        for rec in sim_records:
            qid_b = rec.question_b_id
            if qid_b in user_question_ids or qid_b in exclude_ids:
                continue

            user_score_for_a = user_scores.get(rec.question_a_id, 0)
            question_scores[qid_b] += rec.similarity * user_score_for_a
            question_weights[qid_b] += abs(rec.similarity)

        predictions = []
        for qid, weighted_sum in question_scores.items():
            if question_weights[qid] > 0:
                pred = weighted_sum / question_weights[qid]
                predictions.append((qid, round(pred, 4)))

        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n]

    @staticmethod
    def compute_and_save_all():
        """批量计算并持久化题目相似度矩阵"""
        from apps.questions.models import Question
        try:
            import numpy as np
            from scipy.sparse import csr_matrix
            from sklearn.metrics.pairwise import cosine_similarity
            HAS_NUMPY = True
        except ImportError:
            HAS_NUMPY = False

        if HAS_NUMPY:
            data = list(UserQuestionStatus.objects.values('user_id', 'question_id', 'best_score'))
            if not data:
                return 0

            # 映射 ID 到索引
            user_ids = sorted(list(set(d['user_id'] for d in data)))
            question_ids = sorted(list(set(d['question_id'] for d in data)))

            user_map = {uid: i for i, uid in enumerate(user_ids)}
            question_map = {qid: i for i, qid in enumerate(question_ids)}

            # 构建稀疏矩阵：行是题目，列是用户
            rows = [question_map[d['question_id']] for d in data]
            cols = [user_map[d['user_id']] for d in data]
            scores = [d['best_score'] for d in data]

            matrix = csr_matrix((scores, (rows, cols)), shape=(len(question_ids), len(user_ids)))

            # 计算余弦相似度
            sim_matrix = cosine_similarity(matrix)

            bulk = []
            rows_idx, cols_idx = np.where(sim_matrix > 0)

            for r, c in zip(rows_idx, cols_idx):
                if r >= c:
                    continue

                sim = float(sim_matrix[r, c])
                qid_a = question_ids[r]
                qid_b = question_ids[c]

                bulk.append(QuestionSimilarity(question_a_id=qid_a, question_b_id=qid_b, similarity=sim))
                bulk.append(QuestionSimilarity(question_a_id=qid_b, question_b_id=qid_a, similarity=sim))

            QuestionSimilarity.objects.all().delete()
            QuestionSimilarity.objects.bulk_create(bulk, batch_size=1000)
            return len(bulk) // 2

        # 降级处理
        question_ids = list(Question.objects.values_list('id', flat=True))

        # 构建题目-用户评分矩阵的转置
        item_users = defaultdict(dict)
        for s in UserQuestionStatus.objects.values('user_id', 'question_id', 'best_score'):
            item_users[s['question_id']][s['user_id']] = s['best_score']

        pairs = []
        qids = list(item_users.keys())

        for i in range(len(qids)):
            for j in range(i + 1, len(qids)):
                qa, qb = qids[i], qids[j]
                common_users = set(item_users[qa].keys()) & set(item_users[qb].keys())
                if len(common_users) < 2:
                    continue

                a_vals = [item_users[qa][u] for u in common_users]
                b_vals = [item_users[qb][u] for u in common_users]

                dot = sum(a * b for a, b in zip(a_vals, b_vals))
                norm_a = math.sqrt(sum(a ** 2 for a in a_vals))
                norm_b = math.sqrt(sum(b ** 2 for b in b_vals))

                if norm_a > 0 and norm_b > 0:
                    sim = round(dot / (norm_a * norm_b), 4)
                    if sim > 0:
                        pairs.append((qa, qb, sim))

        QuestionSimilarity.objects.all().delete()
        bulk = []
        for qa, qb, sim in pairs:
            bulk.append(QuestionSimilarity(question_a_id=qa, question_b_id=qb, similarity=sim))
            bulk.append(QuestionSimilarity(question_a_id=qb, question_b_id=qa, similarity=sim))

        QuestionSimilarity.objects.bulk_create(bulk, batch_size=500)
        return len(pairs)