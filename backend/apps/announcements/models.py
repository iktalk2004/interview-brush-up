from django.db import models
from django.conf import settings


class Announcement(models.Model):
    """公告"""
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    is_published = models.BooleanField(default=True, verbose_name='是否发布')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='announcements',
        verbose_name='发布者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'announcements'
        ordering = ['-created_at']
        verbose_name = '公告'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title