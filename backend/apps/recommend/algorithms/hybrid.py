from collections import defaultdict

from .user_cf import UserBasedCF
from .item_cf import ItemBasedCF
from .content_based import ContentBasedRecommender
from .base import BaseRecommender


class HybridRecommender(BaseRecommender):
    """混合推荐：加权融合三种算法"""

    WEIGHTS = {
        'user_cf': 0.4,
        'item_cf': 0.35,
        'content_based': 0.25,
    }

    def get_name(self):
        return 'hybrid'

    def recommend(self, user, n=5, exclude_ids=None):
        exclude_ids = exclude_ids or set()

        algorithms = {
            'user_cf': UserBasedCF(),
            'item_cf': ItemBasedCF(),
            'content_based': ContentBasedRecommender(),
        }

        merged = defaultdict(float)

        for algo_name, algo in algorithms.items():
            weight = self.WEIGHTS[algo_name]
            try:
                results = algo.recommend(user, n=n * 2, exclude_ids=exclude_ids)
                if results:
                    max_score = max(s for _, s in results) if results else 1
                    max_score = max_score if max_score > 0 else 1
                    for qid, score in results:
                        normalized = score / max_score
                        merged[qid] += weight * normalized
            except Exception:
                continue

        predictions = sorted(merged.items(), key=lambda x: x[1], reverse=True)
        return [(qid, round(score, 4)) for qid, score in predictions[:n]]