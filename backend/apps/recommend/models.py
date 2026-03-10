from django.db import models
from django.conf import settings


class DailyRecommendation(models.Model):
    """每日推荐结果"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_recommendations',
        verbose_name='用户'
    )
    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='daily_recommendations',
        verbose_name='推荐题目'
    )
    algorithm = models.CharField(max_length=30, verbose_name='推荐算法')
    score = models.FloatField(default=0, verbose_name='推荐得分')
    is_completed = models.BooleanField(default=False, verbose_name='是否已完成')
    date = models.DateField(verbose_name='推荐日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'daily_recommendations'
        ordering = ['-date', '-score']
        unique_together = ('user', 'question', 'date')
        verbose_name = '每日推荐'
        verbose_name_plural = verbose_name


class UserSimilarity(models.Model):
    """用户相似度矩阵（持久化）"""
    user_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='similarities_as_a',
        verbose_name='用户A'
    )
    user_b = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='similarities_as_b',
        verbose_name='用户B'
    )
    similarity = models.FloatField(default=0, verbose_name='相似度')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'user_similarities'
        unique_together = ('user_a', 'user_b')
        verbose_name = '用户相似度'
        verbose_name_plural = verbose_name


class QuestionSimilarity(models.Model):
    """题目相似度矩阵（持久化）"""
    question_a = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='similarities_as_a',
        verbose_name='题目A'
    )
    question_b = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='similarities_as_b',
        verbose_name='题目B'
    )
    similarity = models.FloatField(default=0, verbose_name='相似度')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'question_similarities'
        unique_together = ('question_a', 'question_b')
        verbose_name = '题目相似度'
        verbose_name_plural = verbose_name