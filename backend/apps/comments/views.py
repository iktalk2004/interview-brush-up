from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from common.response import success_response, error_response, created_response
from apps.questions.models import Question
from apps.users.permissions import IsAdmin
from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer


class CommentListView(APIView):
    """获取题目评论列表"""
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        # 只查顶级评论，回复通过 replies 嵌套返回
        comments = Comment.objects.filter(
            question_id=question_id, parent__isnull=True
        ).select_related('user').prefetch_related('replies__user').order_by('-created_at')

        serializer = CommentSerializer(comments, many=True)
        return success_response(data=serializer.data)


class CommentCreateView(APIView):
    """发表评论/回复"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CommentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message=serializer.errors)

        data = serializer.validated_data
        try:
            question = Question.objects.get(pk=data['question_id'])
        except Question.DoesNotExist:
            return error_response(message='题目不存在')

        parent = None
        parent_id = data.get('parent_id')
        if parent_id:
            try:
                parent = Comment.objects.get(pk=parent_id, question=question)
            except Comment.DoesNotExist:
                return error_response(message='父评论不存在')

        comment = Comment.objects.create(
            user=request.user,
            question=question,
            parent=parent,
            content=data['content'],
        )

        return created_response(data={
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at,
        }, message='评论成功')


class CommentDeleteView(APIView):
    """删除评论（本人或管理员）"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, comment_id):
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return error_response(message='评论不存在')

        if comment.user != request.user and request.user.role != 'admin':
            return error_response(message='无权删除此评论', code=403)

        comment.delete()
        return success_response(message='评论已删除')