from collections import defaultdict

from apps.questions.models import Question
from apps.practice.models import UserQuestionStatus
from apps.users.models import UserInterest
from .base import BaseRecommender


class ContentBasedRecommender(BaseRecommender):
    """基于内容的推荐（含冷启动处理）"""

    def get_name(self):
        return 'content_based'

    def recommend(self, user, n=5, exclude_ids=None):
        exclude_ids = exclude_ids or set()

        user_scores = dict(
            UserQuestionStatus.objects.filter(user=user)
            .values_list('question_id', 'best_score')
        )

        # 冷启动：用户没有答题记录，基于注册兴趣推荐
        if not user_scores:
            return self._cold_start(user, n, exclude_ids)

        user_question_ids = set(user_scores.keys())

        # 分析用户偏好：统计各分类和难度的倾向
        done_questions = Question.objects.filter(id__in=user_question_ids).values(
            'id', 'category_id', 'sub_category_id', 'difficulty'
        )

        cat_weight = defaultdict(float)
        sub_cat_weight = defaultdict(float)
        diff_weight = defaultdict(float)

        for q in done_questions:
            score = user_scores.get(q['id'], 50) / 100
            cat_weight[q['category_id']] += score
            if q['sub_category_id']:
                sub_cat_weight[q['sub_category_id']] += score
            diff_weight[q['difficulty']] += score

        # 对所有未做过的题计算匹配分数
        candidates = Question.objects.exclude(
            id__in=user_question_ids | exclude_ids
        ).values('id', 'category_id', 'sub_category_id', 'difficulty')

        predictions = []
        for q in candidates:
            score = 0
            score += cat_weight.get(q['category_id'], 0) * 0.5
            score += sub_cat_weight.get(q['sub_category_id'], 0) * 0.3
            score += diff_weight.get(q['difficulty'], 0) * 0.2
            if score > 0:
                predictions.append((q['id'], round(score, 4)))

        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n]

    def _cold_start(self, user, n, exclude_ids):
        """冷启动：基于注册兴趣推荐"""
        interests = list(
            UserInterest.objects.filter(user=user).values_list('category_name', flat=True)
        )

        if not interests:
            # 没有兴趣也没有记录，推荐热门简单题
            questions = Question.objects.filter(difficulty='easy').exclude(
                id__in=exclude_ids
            ).order_by('?')[:n]
            return [(q.id, 1.0) for q in questions]

        from apps.questions.models import Category
        cat_ids = list(
            Category.objects.filter(name__in=interests).values_list('id', flat=True)
        )

        questions = Question.objects.filter(category_id__in=cat_ids).exclude(
            id__in=exclude_ids
        ).order_by('?')[:n]

        return [(q.id, 1.0) for q in questions]