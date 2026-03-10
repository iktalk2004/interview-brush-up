from django.db import models
from django.conf import settings


class Collection(models.Model):
    """收藏表"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collections',
        verbose_name='用户'
    )
    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='collections',
        verbose_name='题目'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')

    class Meta:
        db_table = 'collections'
        unique_together = ('user', 'question')
        ordering = ['-created_at']
        verbose_name = '收藏'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username} 收藏 {self.question.title}"