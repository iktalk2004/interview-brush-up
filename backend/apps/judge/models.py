from django.db import models
from django.conf import settings


class JudgeTask(models.Model):
    """判题任务"""

    class Status(models.TextChoices):
        PENDING = 'pending', '等待中'
        RUNNING = 'running', '运行中'
        ACCEPTED = 'accepted', '通过'
        WRONG_ANSWER = 'wrong_answer', '答案错误'
        TIME_LIMIT = 'time_limit', '超时'
        MEMORY_LIMIT = 'memory_limit', '内存超限'
        RUNTIME_ERROR = 'runtime_error', '运行错误'
        COMPILE_ERROR = 'compile_error', '编译错误'
        SYSTEM_ERROR = 'system_error', '系统错误'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='judge_tasks',
        verbose_name='用户'
    )
    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='judge_tasks',
        verbose_name='题目'
    )
    language = models.CharField(max_length=20, verbose_name='编程语言')
    source_code = models.TextField(verbose_name='源代码')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='状态'
    )
    passed_count = models.IntegerField(default=0, verbose_name='通过用例数')
    total_count = models.IntegerField(default=0, verbose_name='总用例数')
    time_used = models.FloatField(default=0, verbose_name='最大运行时间(ms)')
    memory_used = models.FloatField(default=0, verbose_name='最大内存(KB)')
    error_message = models.TextField(blank=True, default='', verbose_name='错误信息')
    detail = models.JSONField(default=list, verbose_name='各用例详细结果')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')

    class Meta:
        db_table = 'judge_tasks'
        ordering = ['-created_at']
        verbose_name = '判题任务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username} - {self.question.title} - {self.status}"