from rest_framework import serializers
from .models import JudgeTask


class SubmitCodeSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    language = serializers.ChoiceField(choices=['python', 'java', 'javascript', 'cpp', 'go', 'c'])
    source_code = serializers.CharField()
    time_spent = serializers.IntegerField(default=0, required=False)


class JudgeTaskSerializer(serializers.ModelSerializer):
    question_title = serializers.CharField(source='question.title', read_only=True)

    class Meta:
        model = JudgeTask
        fields = [
            'id', 'question_id', 'question_title', 'language', 'source_code',
            'status', 'passed_count', 'total_count',
            'time_used', 'memory_used', 'error_message', 'detail',
            'created_at', 'finished_at'
        ]