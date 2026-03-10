from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator

from common.response import success_response, error_response
from apps.questions.models import Question
from .serializers import (
    SubmitTextAnswerSerializer, SubmissionRecordSerializer,
    UserQuestionStatusSerializer,
)
from .services import create_submission_and_update_status
from .models import SubmissionRecord, UserQuestionStatus


class SubmitTextAnswerView(APIView):
    """提交简答题答案"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SubmitTextAnswerSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message=serializer.errors)

        data = serializer.validated_data
        try:
            question = Question.objects.select_related('text_detail').get(
                pk=data['question_id'], question_type='text'
            )
        except Question.DoesNotExist:
            return error_response(message='简答题不存在')

        user_answer = data['user_answer']
        scoring_method = data['scoring_method']
        time_spent = data.get('time_spent', 0)

        # 调用评分引擎
        from apps.scoring.engines.base import SimpleScorer
        from apps.scoring.engines.deepseek import DeepSeekScorer

        if scoring_method == 'deepseek':
            scorer = DeepSeekScorer()
        else:
            scorer = SimpleScorer()

        score, feedback = scorer.score(
            question_title=question.title,
            standard_answer=question.text_detail.standard_answer,
            user_answer=user_answer,
        )

        is_correct = score >= 60

        record = create_submission_and_update_status(
            user=request.user,
            question=question,
            user_answer=user_answer,
            score=score,
            is_correct=is_correct,
            scoring_method=scoring_method,
            time_spent=time_spent,
            ai_feedback=feedback,
        )

        return success_response(data={
            'record_id': record.id,
            'score': record.score,
            'is_correct': record.is_correct,
            'feedback': record.ai_feedback,
            'scoring_method': record.scoring_method,
        }, message='提交成功')


class QuestionHistoryView(APIView):
    """获取某题的历史作答记录"""
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        records = SubmissionRecord.objects.filter(
            user=request.user, question_id=question_id
        ).order_by('-created_at')

        serializer = SubmissionRecordSerializer(records, many=True)
        return success_response(data=serializer.data)


class MistakeListView(APIView):
    """错题本列表"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = UserQuestionStatus.objects.filter(
            user=request.user, is_in_mistake_book=True
        ).select_related('question')

        # 筛选
        category = request.query_params.get('category')
        difficulty = request.query_params.get('difficulty')
        if category:
            queryset = queryset.filter(question__category_id=category)
        if difficulty:
            queryset = queryset.filter(question__difficulty=difficulty)

        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = UserQuestionStatusSerializer(page_obj.object_list, many=True)
        return success_response(data={
            'results': serializer.data,
            'count': paginator.count,
            'page': page,
            'total_pages': paginator.num_pages,
        })


class MistakeRemoveView(APIView):
    """从错题本移除"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, question_id):
        try:
            status = UserQuestionStatus.objects.get(
                user=request.user, question_id=question_id
            )
        except UserQuestionStatus.DoesNotExist:
            return error_response(message='记录不存在')

        status.is_in_mistake_book = False
        status.save()
        return success_response(message='已从错题本移除')


class TopicListView(APIView):
    """专题列表（按分类组织，含进度统计）"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.questions.models import Category, SubCategory, Question

        categories = Category.objects.prefetch_related('sub_categories').all()
        result = []

        for cat in categories:
            cat_total = Question.objects.filter(category=cat).count()
            if cat_total == 0:
                continue

            cat_done = UserQuestionStatus.objects.filter(
                user=request.user, question__category=cat
            ).count()
            cat_correct = UserQuestionStatus.objects.filter(
                user=request.user, question__category=cat, best_score__gte=60
            ).count()

            subs = []
            for sub in cat.sub_categories.all():
                sub_total = Question.objects.filter(sub_category=sub).count()
                if sub_total == 0:
                    continue
                sub_done = UserQuestionStatus.objects.filter(
                    user=request.user, question__sub_category=sub
                ).count()
                sub_correct = UserQuestionStatus.objects.filter(
                    user=request.user, question__sub_category=sub, best_score__gte=60
                ).count()
                subs.append({
                    'id': sub.id,
                    'name': sub.name,
                    'total': sub_total,
                    'done': sub_done,
                    'correct': sub_correct,
                })

            result.append({
                'id': cat.id,
                'name': cat.name,
                'description': cat.description,
                'total': cat_total,
                'done': cat_done,
                'correct': cat_correct,
                'sub_categories': subs,
            })

        return success_response(data=result)


class TopicQuestionsView(APIView):
    """专题练习出题（按分类/子分类获取题目列表，含用户做题状态）"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.questions.models import Question
        from apps.questions.serializers import QuestionListSerializer

        category_id = request.query_params.get('category')
        sub_category_id = request.query_params.get('sub_category')
        difficulty = request.query_params.get('difficulty')
        mode = request.query_params.get('mode', 'order')  # order / random

        queryset = Question.objects.select_related('category', 'sub_category')

        if sub_category_id:
            queryset = queryset.filter(sub_category_id=sub_category_id)
        elif category_id:
            queryset = queryset.filter(category_id=category_id)
        else:
            return error_response(message='请指定分类')

        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        if mode == 'random':
            queryset = queryset.order_by('?')
        else:
            queryset = queryset.order_by('difficulty', 'id')

        questions = queryset[:50]  # 单次最多50题

        # 获取用户状态
        question_ids = [q.id for q in questions]
        statuses = dict(
            UserQuestionStatus.objects.filter(
                user=request.user, question_id__in=question_ids
            ).values_list('question_id', 'best_score')
        )

        serializer = QuestionListSerializer(questions, many=True)
        data = serializer.data
        for item in data:
            item['best_score'] = statuses.get(item['id'])
            item['is_done'] = item['id'] in statuses

        return success_response(data=data)