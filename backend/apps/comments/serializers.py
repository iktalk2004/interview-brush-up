from rest_framework import serializers
from .models import Comment


class ReplySerializer(serializers.ModelSerializer):
    """回复序列化器（第二级）"""
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.SerializerMethodField()
    reply_to = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'username', 'avatar', 'content', 'reply_to', 'created_at']

    def get_avatar(self, obj):
        if obj.user.avatar:
            return obj.user.avatar.url
        return None

    def get_reply_to(self, obj):
        if obj.parent and obj.parent.user:
            return obj.parent.user.username
        return None


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器（第一级，含嵌套回复）"""
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.SerializerMethodField()
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'username', 'avatar', 'content', 'replies', 'created_at']

    def get_avatar(self, obj):
        if obj.user.avatar:
            return obj.user.avatar.url
        return None


class CommentCreateSerializer(serializers.Serializer):
    """创建评论序列化器"""
    question_id = serializers.IntegerField()
    parent_id = serializers.IntegerField(required=False, allow_null=True)
    content = serializers.CharField(max_length=1000)