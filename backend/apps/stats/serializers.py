from rest_framework import serializers
from .models import QuestionStat


class QuestionStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionStat
        fields = [
            'submission_count',
            'success_count',
            'average_score',
            'pass_rate',
            'updated_at',
        ]
