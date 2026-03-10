from django.utils import timezone
from django.conf import settings
from .models import SubmissionRecord, UserQuestionStatus


def create_submission_and_update_status(
    user, question, user_answer, score, is_correct,
    scoring_method, time_spent=0, ai_feedback='', language=''
):
    """
    创建答题记录并同步更新汇总表
    """
    # 1. 创建答题记录
    record = SubmissionRecord.objects.create(
        user=user,
        question=question,
        user_answer=user_answer,
        score=round(score, 2),
        is_correct=is_correct,
        scoring_method=scoring_method,
        time_spent=time_spent,
        ai_feedback=ai_feedback,
        language=language,
    )

    # 2. 更新汇总表
    now = timezone.now()
    status, created = UserQuestionStatus.objects.get_or_create(
        user=user,
        question=question,
        defaults={
            'first_attempt_at': now,
        }
    )

    status.attempt_count += 1
    status.latest_score = round(score, 2)
    status.last_attempt_at = now
    status.total_time_spent += time_spent

    # 更新最高分
    if score > status.best_score:
        status.best_score = round(score, 2)

    # 更新掌握状态（基于最近一次）
    status.is_correct = is_correct

    # 更新错题本状态
    if question.question_type == 'text':
        status.is_in_mistake_book = score < settings.MISTAKE_SCORE_THRESHOLD
    else:
        status.is_in_mistake_book = not is_correct

    if created:
        status.first_attempt_at = now

    status.save()

    return record