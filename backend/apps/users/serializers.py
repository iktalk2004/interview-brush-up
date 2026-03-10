from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserInterest


class RegisterSerializer(serializers.ModelSerializer):
    """注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    interests = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        min_length=1
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'confirm_password',
            'tech_level', 'education', 'github_id', 'interests'
        ]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('用户名已存在')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('邮箱已被注册')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': '两次密码不一致'})
        return attrs

    def create(self, validated_data):
        interests = validated_data.pop('interests')
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        for category_name in interests:
            UserInterest.objects.create(user=user, category_name=category_name)

        return user


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    account = serializers.CharField(help_text='用户名或邮箱')
    password = serializers.CharField()

    def validate(self, attrs):
        account = attrs['account']
        password = attrs['password']

        # 尝试用用户名或邮箱查找用户
        user = User.objects.filter(username=account).first()
        if not user:
            user = User.objects.filter(email=account).first()

        if not user:
            raise serializers.ValidationError('用户不存在')

        if not user.is_active:
            raise serializers.ValidationError('账号已被禁用')

        if not user.check_password(password):
            raise serializers.ValidationError('密码错误')

        attrs['user'] = user
        return attrs


class UserInfoSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    interests = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'avatar', 'github_id',
            'tech_level', 'education', 'role', 'interests',
            'date_joined'
        ]
        read_only_fields = ['id', 'email', 'role', 'date_joined']

    def get_interests(self, obj):
        return list(obj.interests.values_list('category_name', flat=True))


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """个人信息修改序列化器"""
    interests = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'github_id', 'tech_level', 'education', 'interests']

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.filter(username=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError('用户名已存在')
        return value

    def update(self, instance, validated_data):
        interests = validated_data.pop('interests', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if interests is not None:
            instance.interests.all().delete()
            for category_name in interests:
                UserInterest.objects.create(user=instance, category_name=category_name)

        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码错误')
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    """发送验证码序列化器"""
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('该邮箱未注册')
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """重置密码序列化器"""
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)


class AvatarUploadSerializer(serializers.ModelSerializer):
    """头像上传序列化器"""
    class Meta:
        model = User
        fields = ['avatar']

    def validate_avatar(self, value):
        from django.conf import settings
        if value.size > settings.MAX_AVATAR_SIZE:
            raise serializers.ValidationError('头像文件不能超过2MB')
        return value