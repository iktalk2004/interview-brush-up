from rest_framework import serializers
from .models import Announcement


class AnnouncementListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True, default='')

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'is_published', 'author_name', 'created_at', 'updated_at']


class AnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'is_published']