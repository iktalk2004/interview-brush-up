import math
from collections import defaultdict
from django.db.models import Avg

from apps.practice.models import UserQuestionStatus
from apps.recommend.models import UserSimilarity
from .base import BaseRecommender


class UserBasedCF(BaseRecommender):
    """基于用户的协同过滤"""

    def get_name(self):
        return 'user_cf'

    def recommend(self, user, n=5, exclude_ids=None):
        exclude_ids = exclude_ids or set()

        # 获取目标用户的答题记录 {question_id: best_score}
        user_scores = dict(
            UserQuestionStatus.objects.filter(user=user)
            .values_list('question_id', 'best_score')
        )
        if not user_scores:
            return []

        user_question_ids = set(user_scores.keys())

        # 获取相似用户（从持久化表读取）
        similarities = UserSimilarity.objects.filter(
            user_a=user, similarity__gt=0
        ).order_by('-similarity')[:20]

        if not similarities:
            # 如果没有预计算的相似度，实时计算
            similarities = self._compute_similarities(user, user_scores)

        # 加权预测分数
        question_scores = defaultdict(float)
        question_weights = defaultdict(float)

        for sim in similarities:
            neighbor = sim.user_b if hasattr(sim, 'user_b') else sim['user_b']
            sim_value = sim.similarity if hasattr(sim, 'similarity') else sim['similarity']

            neighbor_id = neighbor.id if hasattr(neighbor, 'id') else neighbor

            neighbor_scores = dict(
                UserQuestionStatus.objects.filter(user_id=neighbor_id)
                .values_list('question_id', 'best_score')
            )

            for qid, score in neighbor_scores.items():
                if qid not in user_question_ids and qid not in exclude_ids:
                    question_scores[qid] += sim_value * score
                    question_weights[qid] += abs(sim_value)

        # 计算预测分并排序
        predictions = []
        for qid, weighted_sum in question_scores.items():
            if question_weights[qid] > 0:
                pred = weighted_sum / question_weights[qid]
                predictions.append((qid, round(pred, 4)))

        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n]

    def _compute_similarities(self, user, user_scores):
        """实时计算用户相似度（余弦相似度）"""
        all_statuses = UserQuestionStatus.objects.exclude(user=user).values(
            'user_id', 'question_id', 'best_score'
        )

        other_users = defaultdict(dict)
        for s in all_statuses:
            other_users[s['user_id']][s['question_id']] = s['best_score']

        results = []
        for other_id, other_scores in other_users.items():
            common = set(user_scores.keys()) & set(other_scores.keys())
            if len(common) < 2:
                continue

            a_vals = [user_scores[q] for q in common]
            b_vals = [other_scores[q] for q in common]

            dot = sum(a * b for a, b in zip(a_vals, b_vals))
            norm_a = math.sqrt(sum(a ** 2 for a in a_vals))
            norm_b = math.sqrt(sum(b ** 2 for b in b_vals))

            if norm_a > 0 and norm_b > 0:
                sim = dot / (norm_a * norm_b)
                results.append({'user_b': other_id, 'similarity': round(sim, 4)})

        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:20]

    @staticmethod
    def compute_and_save_all():
        """批量计算并持久化用户相似度矩阵"""
        from apps.users.models import User

        users = list(User.objects.filter(is_active=True, role='user'))
        user_data = {}

        for u in users:
            scores = dict(
                UserQuestionStatus.objects.filter(user=u)
                .values_list('question_id', 'best_score')
            )
            if scores:
                user_data[u.id] = scores

        user_ids = list(user_data.keys())
        pairs = []

        for i in range(len(user_ids)):
            for j in range(i + 1, len(user_ids)):
                uid_a, uid_b = user_ids[i], user_ids[j]
                common = set(user_data[uid_a].keys()) & set(user_data[uid_b].keys())
                if len(common) < 2:
                    continue

                a_vals = [user_data[uid_a][q] for q in common]
                b_vals = [user_data[uid_b][q] for q in common]

                dot = sum(a * b for a, b in zip(a_vals, b_vals))
                norm_a = math.sqrt(sum(a ** 2 for a in a_vals))
                norm_b = math.sqrt(sum(b ** 2 for b in b_vals))

                if norm_a > 0 and norm_b > 0:
                    sim = round(dot / (norm_a * norm_b), 4)
                    if sim > 0:
                        pairs.append((uid_a, uid_b, sim))

        UserSimilarity.objects.all().delete()
        bulk = []
        for uid_a, uid_b, sim in pairs:
            bulk.append(UserSimilarity(user_a_id=uid_a, user_b_id=uid_b, similarity=sim))
            bulk.append(UserSimilarity(user_a_id=uid_b, user_b_id=uid_a, similarity=sim))

        UserSimilarity.objects.bulk_create(bulk, batch_size=500)
        return len(pairs)