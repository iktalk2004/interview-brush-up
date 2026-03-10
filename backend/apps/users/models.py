from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """自定义用户模型"""

    class TechLevel(models.TextChoices):
        BEGINNER = 'beginner', '初级',
        INTERMEDIATE = 'intermediate', '中级',
        ADVANCED = 'advanced', '高级',

    class Education(models.TextChoices):
        COLLEGE = 'college', '大专'
        BACHELOR = 'bachelor', '本科'
        MASTER = 'master', '硕士'
        DOCTOR = 'doctor', '博士'
        OTHER = 'other', '其他'

    class Role(models.TextChoices):
        USER = 'user', '普通用户'
        ADMIN = 'admin', '管理员'

    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    github_id = models.CharField(max_length=100, blank=True, default='', verbose_name='GitHub ID')
    tech_level = models.CharField(
        max_length=20,
        choices=TechLevel.choices,
        default=TechLevel.BEGINNER,
        verbose_name='技术水平'
    )
    education = models.CharField(
        max_length=20,
        choices=Education.choices,
        blank=True,
        default='',
        verbose_name='学历'
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='角色'
    )

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class UserInterest(models.Model):
    """用户兴趣关联表"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='interests',
        verbose_name='用户'
    )
    # 这里先用 CharField 存储分类名称
    # 等阶段三 Category 模型建好后，再改为 ForeignKey
    category_name = models.CharField(max_length=50, verbose_name='兴趣分类名称')

    class Meta:
        db_table = 'user_interests'
        verbose_name = '用户兴趣'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'category_name')
    
    def __str__(self):
        return f'{self.user.username} - {self.category_name}'



