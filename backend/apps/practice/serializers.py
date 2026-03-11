from rest_framework import serializers
from .models import SubmissionRecord, UserQuestionStatus


class SubmitTextAnswerSerializer(serializers.Serializer):
    """简答题提交序列化器"""
    question_id = serializers.IntegerField()
    user_answer = serializers.CharField()
    scoring_method = serializers.ChoiceField(choices=['model', 'deepseek'])
    time_spent = serializers.IntegerField(default=0, required=False)


class SubmissionRecordSerializer(serializers.ModelSerializer):
    """答题记录序列化器"""
    question_title = serializers.CharField(source='question.title', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)

    class Meta:
        model = SubmissionRecord
        fields = [
            'id', 'question_id', 'question_title', 'question_type', 'user_answer',
            'score', 'is_correct', 'scoring_method', 'language',
            'time_spent', 'ai_feedback', 'created_at'
        ]


class UserQuestionStatusSerializer(serializers.ModelSerializer):
    """用户题目状态序列化器"""
    question_title = serializers.CharField(source='question.title', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)

    class Meta:
        model = UserQuestionStatus
        fields = [
            'id', 'question_id', 'question_title', 'question_type',
            'attempt_count', 'best_score', 'latest_score',
            'is_correct', 'is_in_mistake_book',
            'first_attempt_at', 'last_attempt_at', 'total_time_spent'
        ]
