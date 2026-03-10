from django.db import models


class Category(models.Model):
    """一级分类（岗位方向）"""
    name = models.CharField(max_length=50, unique=True, verbose_name='分类名称')
    description = models.TextField(blank=True, default='', verbose_name='描述')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'categories'
        ordering = ['sort_order', 'id']
        verbose_name = '一级分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    """二级分类（知识领域）"""
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='sub_categories',
        verbose_name='所属一级分类'
    )
    name = models.CharField(max_length=50, verbose_name='子分类名称')
    description = models.TextField(blank=True, default='', verbose_name='描述')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'sub_categories'
        ordering = ['sort_order', 'id']
        unique_together = ('category', 'name')
        verbose_name = '二级分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Question(models.Model):
    """题目基础表"""

    class QuestionType(models.TextChoices):
        TEXT = 'text', '简答题'
        CODE = 'code', '代码题'

    class Difficulty(models.TextChoices):
        EASY = 'easy', '简单'
        MEDIUM = 'medium', '中等'
        HARD = 'hard', '困难'

    question_type = models.CharField(
        max_length=10,
        choices=QuestionType.choices,
        verbose_name='题目类型'
    )
    title = models.CharField(max_length=255, verbose_name='题目标题')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='questions',
        verbose_name='一级分类'
    )
    sub_category = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='questions',
        verbose_name='二级分类'
    )
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.MEDIUM,
        verbose_name='难度等级'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'questions'
        ordering = ['-created_at']
        verbose_name = '题目'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class TextQuestionDetail(models.Model):
    """简答题扩展表"""
    question = models.OneToOneField(
        Question,
        on_delete=models.CASCADE,
        related_name='text_detail',
        verbose_name='关联题目'
    )
    content = models.TextField(blank=True, default='', verbose_name='题干补充')
    standard_answer = models.TextField(verbose_name='标准答案')
    explanation = models.TextField(blank=True, default='', verbose_name='详细解析')

    class Meta:
        db_table = 'text_question_details'
        verbose_name = '简答题详情'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"简答题详情 - {self.question.title}"


class CodeQuestionDetail(models.Model):
    """代码题扩展表"""
    question = models.OneToOneField(
        Question,
        on_delete=models.CASCADE,
        related_name='code_detail',
        verbose_name='关联题目'
    )
    description = models.TextField(verbose_name='题目描述')
    test_cases = models.JSONField(default=list, verbose_name='测试用例')
    reference_code = models.TextField(blank=True, default='', verbose_name='参考代码')
    code_template = models.JSONField(default=dict, blank=True, verbose_name='代码模板')
    time_limit = models.IntegerField(default=1000, verbose_name='时间限制(ms)')
    memory_limit = models.IntegerField(default=256, verbose_name='内存限制(MB)')

    class Meta:
        db_table = 'code_question_details'
        verbose_name = '代码题详情'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"代码题详情 - {self.question.title}"