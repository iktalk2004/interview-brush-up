from rest_framework import serializers
from .models import Collection
from apps.questions.serializers import QuestionListSerializer


class CollectionSerializer(serializers.ModelSerializer):
    """收藏序列化器"""
    question = QuestionListSerializer(read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'question', 'created_at']