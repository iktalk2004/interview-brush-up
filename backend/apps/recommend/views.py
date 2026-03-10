from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.conf import settings

from common.response import success_response, error_response
from apps.users.permissions import IsAdmin
from apps.questions.models import Question
from apps.questions.serializers import QuestionListSerializer
from .models import DailyRecommendation
from .algorithms import UserBasedCF, ItemBasedCF, ContentBasedRecommender, HybridRecommender


class HomeRecommendView(APIView):
    """首页推荐"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        algo = HybridRecommender()
        from apps.practice.models import UserQuestionStatus

        done_ids = set(
            UserQuestionStatus.objects.filter(user=request.user)
            .values_list('question_id', flat=True)
        )

        results = algo.recommend(request.user, n=6, exclude_ids=done_ids)
        question_ids = [qid for qid, _ in results]

        if not question_ids:
            questions = Question.objects.order_by('?')[:6]
        else:
            questions = Question.objects.filter(id__in=question_ids).select_related('category', 'sub_category')

        serializer = QuestionListSerializer(questions, many=True)
        return success_response(data=serializer.data)


class DailyRecommendView(APIView):
    """每日推荐"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()

        # 查看今天是否已有推荐
        daily = DailyRecommendation.objects.filter(
            user=request.user, date=today
        ).select_related('question__category', 'question__sub_category')

        if daily.exists():
            data = []
            for rec in daily:
                q_data = QuestionListSerializer(rec.question).data
                q_data['is_completed'] = rec.is_completed
                q_data['algorithm'] = rec.algorithm
                data.append(q_data)
            return success_response(data=data)

        # 没有则实时生成
        algo = HybridRecommender()
        from apps.practice.models import UserQuestionStatus

        done_ids = set(
            UserQuestionStatus.objects.filter(user=request.user)
            .values_list('question_id', flat=True)
        )

        count = getattr(settings, 'DAILY_RECOMMEND_COUNT', 5)
        results = algo.recommend(request.user, n=count, exclude_ids=done_ids)

        if not results:
            questions = Question.objects.exclude(id__in=done_ids).order_by('?')[:count]
            results = [(q.id, 1.0) for q in questions]

        records = []
        for qid, score in results:
            rec, _ = DailyRecommendation.objects.get_or_create(
                user=request.user, question_id=qid, date=today,
                defaults={'algorithm': 'hybrid', 'score': score}
            )
            records.append(rec)

        data = []
        for rec in records:
            try:
                q = Question.objects.select_related('category', 'sub_category').get(pk=rec.question_id)
                q_data = QuestionListSerializer(q).data
                q_data['is_completed'] = rec.is_completed
                q_data['algorithm'] = rec.algorithm
                data.append(q_data)
            except Question.DoesNotExist:
                continue

        return success_response(data=data)


class AdminAlgorithmCompareView(APIView):
    """管理员 - 算法对比"""
    permission_classes = [IsAdmin]

    def get(self, request):
        from apps.users.models import User
        from .evaluator import evaluate_algorithm

        users = list(User.objects.filter(is_active=True, role='user'))

        algorithms = {
            'User-based CF': UserBasedCF(),
            'Item-based CF': ItemBasedCF(),
            'Content-based': ContentBasedRecommender(),
            'Hybrid': HybridRecommender(),
        }

        results = {}
        for name, algo in algorithms.items():
            metrics = evaluate_algorithm(algo, users, k=5)
            results[name] = metrics

        return success_response(data=results)


class AdminTriggerSimilarityView(APIView):
    """管理员 - 手动触发相似度计算"""
    permission_classes = [IsAdmin]

    def post(self, request):
        user_pairs = UserBasedCF.compute_and_save_all()
        item_pairs = ItemBasedCF.compute_and_save_all()
        return success_response(data={
            'user_similarity_pairs': user_pairs,
            'item_similarity_pairs': item_pairs,
        }, message='相似度计算完成')