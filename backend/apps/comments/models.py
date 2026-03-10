from django.db import models
from django.conf import settings


class Comment(models.Model):
    """评论表（支持嵌套回复）"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='评论者'
    )
    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='所属题目'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='父评论'
    )
    content = models.TextField(verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')

    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']
        verbose_name = '评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"