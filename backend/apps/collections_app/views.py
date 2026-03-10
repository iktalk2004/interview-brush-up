from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator

from common.response import success_response, error_response, created_response
from apps.questions.models import Question
from .models import Collection
from .serializers import CollectionSerializer


class CollectionListView(APIView):
    """收藏列表 & 添加收藏"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Collection.objects.filter(
            user=request.user
        ).select_related('question__category', 'question__sub_category')

        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = CollectionSerializer(page_obj.object_list, many=True)
        return success_response(data={
            'results': serializer.data,
            'count': paginator.count,
            'page': page,
            'total_pages': paginator.num_pages,
        })

    def post(self, request):
        question_id = request.data.get('question_id')
        if not question_id:
            return error_response(message='缺少 question_id')

        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            return error_response(message='题目不存在')

        _, created = Collection.objects.get_or_create(user=request.user, question=question)
        if not created:
            return error_response(message='已收藏该题目')

        return created_response(message='收藏成功')


class CollectionRemoveView(APIView):
    """取消收藏"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, question_id):
        deleted, _ = Collection.objects.filter(
            user=request.user, question_id=question_id
        ).delete()

        if deleted:
            return success_response(message='已取消收藏')
        return error_response(message='未收藏该题目')


class CollectionCheckView(APIView):
    """检查是否已收藏某题"""
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        is_collected = Collection.objects.filter(
            user=request.user, question_id=question_id
        ).exists()
        return success_response(data={'is_collected': is_collected})