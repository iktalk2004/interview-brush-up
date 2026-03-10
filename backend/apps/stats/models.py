from django.db import models
from django.conf import settings


class PageVisitLog(models.Model):
    """页面停留时长记录"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='visit_logs',
        verbose_name='用户'
    )
    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='visit_logs',
        verbose_name='题目'
    )
    duration = models.IntegerField(default=0, verbose_name='停留时长(秒)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='记录时间')

    class Meta:
        db_table = 'page_visit_logs'
        ordering = ['-created_at']
        verbose_name = '页面停留记录'
        verbose_name_plural = verbose_name