from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from common.response import success_response, error_response
from apps.users.permissions import IsAdmin
from .models import PageVisitLog, QuestionStat
from .services import get_user_dashboard, get_ranking_list, update_question_stat, update_all_question_stats


class DashboardView(APIView):
    """个人看板数据"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_user_dashboard(request.user)
        return success_response(data=data)


class LearningTimeReportView(APIView):
    """学习时长上报"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        question_id = request.data.get('question_id')
        duration = request.data.get('duration', 0)

        if not isinstance(duration, int) or duration <= 0:
            return error_response(message='时长参数无效')

        PageVisitLog.objects.create(
            user=request.user,
            question_id=question_id,
            duration=duration,
        )
        return success_response(message='上报成功')


class RankingView(APIView):
    """排行榜"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', 'all')
        metric = request.query_params.get('metric', 'count')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        data = get_ranking_list(period=period, metric=metric, page=page, page_size=page_size)
        return success_response(data=data)


class PracticeHistoryView(APIView):
    """刷题记录"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.core.paginator import Paginator
        from apps.practice.models import SubmissionRecord
        from apps.practice.serializers import SubmissionRecordSerializer

        queryset = SubmissionRecord.objects.filter(
            user=request.user
        ).select_related('question').order_by('-created_at')

        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = SubmissionRecordSerializer(page_obj.object_list, many=True)
        return success_response(data={
            'results': serializer.data,
            'count': paginator.count,
            'page': page,
            'total_pages': paginator.num_pages,
        })


# ============================================================
# 管理员统计接口
# ============================================================

class AdminStatsOverviewView(APIView):
    """管理员 - 系统统计概览"""
    permission_classes = [IsAdmin]

    def get(self, request):
        from apps.users.models import User
        from apps.questions.models import Question
        from apps.practice.models import SubmissionRecord
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count
        from django.db.models.functions import TruncDate

        # 基础统计
        data = {
            'total_users': User.objects.filter(is_active=True).count(),
            'total_questions': Question.objects.count(),
            'total_submissions': SubmissionRecord.objects.count(),
            'text_questions': Question.objects.filter(question_type='text').count(),
            'code_questions': Question.objects.filter(question_type='code').count(),
        }

        # 近14天提交趋势
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=13)
        daily_data = (
            SubmissionRecord.objects
            .filter(created_at__date__gte=start_date)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        daily_map = {str(item['date']): item['count'] for item in daily_data}
        trend = []
        for i in range(14):
            d = start_date + timedelta(days=i)
            trend.append({
                'date': str(d),
                'count': daily_map.get(str(d), 0),
            })
        data['submission_trend'] = trend

        # 近14天新增用户趋势
        user_daily = (
            User.objects
            .filter(date_joined__date__gte=start_date)
            .annotate(date=TruncDate('date_joined'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        user_map = {str(item['date']): item['count'] for item in user_daily}
        user_trend = []
        for i in range(14):
            d = start_date + timedelta(days=i)
            user_trend.append({
                'date': str(d),
                'count': user_map.get(str(d), 0),
            })
        data['user_trend'] = user_trend

        return success_response(data=data)


class QuestionStatView(APIView):
    """获取题目统计数据"""
    permission_classes = []

    def get(self, request):
        question_id = request.query_params.get('question_id')
        if not question_id:
            return error_response(message='缺少question_id参数')
        
        try:
            stat = QuestionStat.objects.get(question_id=question_id)
            from .serializers import QuestionStatSerializer
            serializer = QuestionStatSerializer(stat)
            return success_response(data=serializer.data)
        except QuestionStat.DoesNotExist:
            return success_response(data={
                'submission_count': 0,
                'success_count': 0,
                'average_score': 0.0,
                'pass_rate': 0.0,
            })


class BatchUpdateQuestionStatsView(APIView):
    """批量更新题目统计数据（管理员）"""
    permission_classes = [IsAdmin]

    def post(self, request):
        question_id = request.data.get('question_id')
        
        if question_id:
            update_question_stat(question_id)
            return success_response(message='题目统计更新成功')
        else:
            update_all_question_stats()
            return success_response(message='全部题目统计更新成功')