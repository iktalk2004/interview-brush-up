from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta

from apps.practice.models import UserQuestionStatus, SubmissionRecord
from apps.questions.models import Category


def get_user_dashboard(user):
    """获取用户个人看板数据"""
    statuses = UserQuestionStatus.objects.filter(user=user)

    # 刷题总数（去重题目数）
    total_questions = statuses.count()

    # 正确率（取每道题最优成绩，best_score >= 60 视为正确）
    correct_count = statuses.filter(best_score__gte=60).count()
    accuracy = round(correct_count / total_questions * 100, 2) if total_questions > 0 else 0

    # 累计学习时长
    total_time = statuses.aggregate(t=Sum('total_time_spent'))['t'] or 0

    # 今日数据
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_submissions = SubmissionRecord.objects.filter(user=user, created_at__gte=today_start)
    today_count = today_submissions.values('question_id').distinct().count()
    today_time = today_submissions.aggregate(t=Sum('time_spent'))['t'] or 0

    # 各分类掌握度（用于雷达图）
    category_stats = []
    categories = Category.objects.all()
    for cat in categories:
        cat_statuses = statuses.filter(question__category=cat)
        cat_total = cat_statuses.count()
        if cat_total > 0:
            cat_correct = cat_statuses.filter(best_score__gte=60).count()
            mastery = round(cat_correct / cat_total * 100, 1)
        else:
            mastery = 0
        category_stats.append({
            'category_id': cat.id,
            'category_name': cat.name,
            'total': cat_total,
            'correct': cat_statuses.filter(best_score__gte=60).count() if cat_total > 0 else 0,
            'mastery': mastery,
        })

    return {
        'total_questions': total_questions,
        'correct_count': correct_count,
        'accuracy': accuracy,
        'total_time': total_time,
        'today_count': today_count,
        'today_time': today_time,
        'category_stats': category_stats,
    }


def get_ranking_list(period='all', metric='count', page=1, page_size=20):
    """获取排行榜"""
    from apps.users.models import User

    # 确定时间范围
    now = timezone.now()
    if period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    else:
        start_date = None

    # 基础查询
    users = User.objects.filter(is_active=True, role='user')

    ranking = []
    for user in users:
        statuses = UserQuestionStatus.objects.filter(user=user)
        if start_date:
            statuses = statuses.filter(last_attempt_at__gte=start_date)

        total = statuses.count()
        if total == 0:
            continue

        correct = statuses.filter(best_score__gte=60).count()
        accuracy = round(correct / total * 100, 2) if total > 0 else 0

        ranking.append({
            'user_id': user.id,
            'username': user.username,
            'avatar': user.avatar.url if user.avatar else None,
            'total_questions': total,
            'accuracy': accuracy,
        })

    # 排序
    if metric == 'count':
        ranking.sort(key=lambda x: x['total_questions'], reverse=True)
    else:
        ranking.sort(key=lambda x: x['accuracy'], reverse=True)

    # 添加排名
    for i, item in enumerate(ranking):
        item['rank'] = i + 1

    # 分页
    total_count = len(ranking)
    start = (page - 1) * page_size
    end = start + page_size

    return {
        'results': ranking[start:end],
        'count': total_count,
        'page': page,
        'total_pages': (total_count + page_size - 1) // page_size,
    }