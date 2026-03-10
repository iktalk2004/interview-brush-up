import django_filters
from .models import Question


class QuestionFilter(django_filters.FilterSet):
    """题目筛选器"""
    category = django_filters.NumberFilter(field_name='category_id')
    sub_category = django_filters.NumberFilter(field_name='sub_category_id')
    difficulty = django_filters.CharFilter(field_name='difficulty')
    question_type = django_filters.CharFilter(field_name='question_type')

    class Meta:
        model = Question
        fields = ['category', 'sub_category', 'difficulty', 'question_type']