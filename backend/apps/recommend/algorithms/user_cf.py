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
        similarities = list(UserSimilarity.objects.filter(
            user_a=user, similarity__gt=0
        ).order_by('-similarity')[:20])

        if not similarities:
            # 如果没有预计算的相似度，实时计算
            similarities = self._compute_similarities(user, user_scores)

        # 批量获取相似用户的答题记录，避免 N+1 查询
        neighbor_ids = []
        sim_map = {}
        for sim in similarities:
            if isinstance(sim, dict):
                nid = sim['user_b']
                s = sim['similarity']
            else:
                nid = sim.user_b_id
                s = sim.similarity
            neighbor_ids.append(nid)
            sim_map[nid] = s

        if not neighbor_ids:
            return []

        # 一次性查询所有相似用户的答题记录
        neighbor_records = UserQuestionStatus.objects.filter(
            user_id__in=neighbor_ids
        ).values('user_id', 'question_id', 'best_score')

        # 加权预测分数
        question_scores = defaultdict(float)
        question_weights = defaultdict(float)

        for record in neighbor_records:
            qid = record['question_id']
            uid = record['user_id']
            score = record['best_score']

            if qid in user_question_ids or qid in exclude_ids:
                continue

            sim_val = sim_map.get(uid, 0)
            question_scores[qid] += sim_val * score
            question_weights[qid] += abs(sim_val)

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
        # 仅计算近期活跃用户的相似度，避免全量扫描
        # 或者限制数量
        all_statuses = UserQuestionStatus.objects.exclude(user=user).values(
            'user_id', 'question_id', 'best_score'
        )[:5000]  # 限制样本数量防止 OOM

        other_users = defaultdict(dict)
        for s in all_statuses:
            other_users[s['user_id']][s['question_id']] = s['best_score']

        results = []
        user_vector_norm = math.sqrt(sum(s ** 2 for s in user_scores.values()))

        if user_vector_norm == 0:
            return []

        for other_id, other_scores in other_users.items():
            common = set(user_scores.keys()) & set(other_scores.keys())
            if not common:
                continue

            # 优化点积计算
            dot = sum(user_scores[q] * other_scores[q] for q in common)
            norm_b = math.sqrt(sum(s ** 2 for s in other_scores.values()))

            if norm_b > 0:
                sim = dot / (user_vector_norm * norm_b)
                results.append({'user_b': other_id, 'similarity': round(sim, 4)})

        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:20]

    @staticmethod
    def compute_and_save_all():
        """批量计算并持久化用户相似度矩阵"""
        from apps.users.models import User
        try:
            import numpy as np
            from scipy.sparse import csr_matrix
            from sklearn.metrics.pairwise import cosine_similarity
            HAS_NUMPY = True
        except ImportError:
            HAS_NUMPY = False

        if HAS_NUMPY:
            # 使用 Numpy/Scikit-learn 加速计算
            data = list(UserQuestionStatus.objects.values('user_id', 'question_id', 'best_score'))
            if not data:
                return 0

            # 映射 ID 到索引
            user_ids = sorted(list(set(d['user_id'] for d in data)))
            question_ids = sorted(list(set(d['question_id'] for d in data)))
            
            user_map = {uid: i for i, uid in enumerate(user_ids)}
            question_map = {qid: i for i, qid in enumerate(question_ids)}
            
            rows = [user_map[d['user_id']] for d in data]
            cols = [question_map[d['question_id']] for d in data]
            scores = [d['best_score'] for d in data]
            
            # 构建稀疏矩阵
            matrix = csr_matrix((scores, (rows, cols)), shape=(len(user_ids), len(question_ids)))
            
            # 计算余弦相似度
            sim_matrix = cosine_similarity(matrix)
            
            # 提取结果
            bulk = []
            # 仅保存上三角矩阵（避免重复），且相似度 > 0
            # 获取非零元素的索引
            # 注意：cosine_similarity 返回的是稠密矩阵，如果用户量巨大可能需要分块处理
            # 这里假设用户量在可控范围内 (< 10000)
            
            rows_idx, cols_idx = np.where(sim_matrix > 0)
            
            for r, c in zip(rows_idx, cols_idx):
                if r >= c: # 避免重复和自相似
                    continue
                    
                sim = float(sim_matrix[r, c])
                uid_a = user_ids[r]
                uid_b = user_ids[c]
                
                bulk.append(UserSimilarity(user_a_id=uid_a, user_b_id=uid_b, similarity=sim))
                bulk.append(UserSimilarity(user_a_id=uid_b, user_b_id=uid_a, similarity=sim))
                
            UserSimilarity.objects.all().delete()
            UserSimilarity.objects.bulk_create(bulk, batch_size=1000)
            return len(bulk) // 2

        # 降级到纯 Python 实现 (保留原有逻辑但稍作优化)
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