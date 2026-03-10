from django.db import models
from django.conf import settings


class SubmissionRecord(models.Model):
    """答题记录表（保留全部记录）"""

    class ScoringMethod(models.TextChoices):
        MODEL = 'model', '内嵌模型评分'
        DEEPSEEK = 'deepseek', 'DeepSeek API评分'
        JUDGE = 'judge', '代码判题'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='用户'
    )
    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='题目'
    )
    user_answer = models.TextField(verbose_name='用户答案/代码')
    score = models.FloatField(default=0, verbose_name='评分(0-100)')
    is_correct = models.BooleanField(default=False, verbose_name='是否正确/通过')
    scoring_method = models.CharField(
        max_length=20,
        choices=ScoringMethod.choices,
        verbose_name='评分方式'
    )
    language = models.CharField(max_length=20, blank=True, default='', verbose_name='编程语言')
    time_spent = models.IntegerField(default=0, verbose_name='答题耗时(秒)')
    ai_feedback = models.TextField(blank=True, default='', verbose_name='AI评语')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')

    class Meta:
        db_table = 'submission_records'
        ordering = ['-created_at']
        verbose_name = '答题记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username} - {self.question.title} - {self.score}"


class UserQuestionStatus(models.Model):
    """用户题目状态汇总表"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='question_statuses',
        verbose_name='用户'
    )
    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='user_statuses',
        verbose_name='题目'
    )
    attempt_count = models.IntegerField(default=0, verbose_name='提交次数')
    best_score = models.FloatField(default=0, verbose_name='历史最高分')
    latest_score = models.FloatField(default=0, verbose_name='最近一次得分')
    is_correct = models.BooleanField(default=False, verbose_name='是否已掌握(基于最近一次)')
    is_in_mistake_book = models.BooleanField(default=False, verbose_name='是否在错题本中')
    first_attempt_at = models.DateTimeField(null=True, blank=True, verbose_name='首次作答时间')
    last_attempt_at = models.DateTimeField(null=True, blank=True, verbose_name='最近作答时间')
    total_time_spent = models.IntegerField(default=0, verbose_name='累计答题耗时(秒)')

    class Meta:
        db_table = 'user_question_status'
        unique_together = ('user', 'question')
        verbose_name = '用户题目状态'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username} - {self.question.title} - 最高{self.best_score}"