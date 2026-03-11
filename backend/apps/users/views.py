from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from common.response import success_response, error_response, created_response
from .serializers import (
    RegisterSerializer, LoginSerializer, UserInfoSerializer,
    UserProfileUpdateSerializer, ChangePasswordSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer, AvatarUploadSerializer,
)
from .utils import send_verification_code, verify_code
from .models import User
from .permissions import IsAdmin


class RegisterView(APIView):
    """用户注册"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message=serializer.errors)

        user = serializer.save()

        # 注册成功自动签发Token
        refresh = RefreshToken.for_user(user)
        user_info = UserInfoSerializer(user).data

        return created_response(data={
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_info,
        }, message='注册成功')


class LoginView(APIView):
    """用户登录"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message=serializer.errors)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        user_info = UserInfoSerializer(user).data

        return success_response(data={
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_info,
        }, message='登录成功')


class TokenRefreshView(APIView):
    """刷新Token"""
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return error_response(message='缺少refresh token')

        try:
            refresh = RefreshToken(refresh_token)
            return success_response(data={
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        except Exception:
            return error_response(message='Token无效或已过期', code=401)


class ForgotPasswordView(APIView):
    """发送验证码"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message=serializer.errors)

        email = serializer.validated_data['email']
        ok, msg = send_verification_code(email)

        if ok:
            return success_response(message=msg)
        return error_response(message=msg)


class ResetPasswordView(APIView):
    """重置密码"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message=serializer.errors)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']

        ok, msg = verify_code(email, code)
        if not ok:
            return error_response(message=msg)

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            return success_response(message='密码重置成功')
        except User.DoesNotExist:
            return error_response(message='用户不存在')


class UserProfileView(APIView):
    """获取/修改个人信息"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserInfoSerializer(request.user)
        return success_response(data=serializer.data)

    def put(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if not serializer.is_valid():
            return error_response(message=serializer.errors)

        serializer.save()

        # 修改资料（特别是兴趣）后，清除当天的推荐记录，以便重新生成
        try:
            from apps.recommend.models import DailyRecommendation
            from django.utils import timezone
            DailyRecommendation.objects.filter(
                user=request.user, 
                date=timezone.now().date(),
                is_completed=False  # 仅清除未完成的
            ).delete()
        except Exception:
            pass

        user_info = UserInfoSerializer(request.user).data
        return success_response(data=user_info, message='修改成功')


class ChangePasswordView(APIView):
    """修改密码"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return error_response(message=serializer.errors)

        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return success_response(message='密码修改成功')


class AvatarUploadView(APIView):
    """头像上传"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AvatarUploadSerializer(request.user, data=request.data)
        if not serializer.is_valid():
            return error_response(message=serializer.errors)

        serializer.save()
        return success_response(
            data={'avatar': request.user.avatar.url if request.user.avatar else None},
            message='头像上传成功'
        )


# ============================================================
# 管理员接口
# ============================================================

class AdminUserListView(APIView):
    """管理员 - 用户列表"""
    permission_classes = [IsAdmin]

    def get(self, request):
        from django.core.paginator import Paginator

        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        search = request.query_params.get('search', '')

        queryset = User.objects.all().order_by('id')
        if search:
            queryset = queryset.filter(
                models.Q(username__icontains=search) | models.Q(email__icontains=search)
            )

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        users = UserInfoSerializer(page_obj.object_list, many=True).data
        return success_response(data={
            'results': users,
            'count': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
        })


class AdminUserStatusView(APIView):
    """管理员 - 禁用/启用用户"""
    permission_classes = [IsAdmin]

    def put(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return error_response(message='用户不存在', code=404)

        if user.role == 'admin':
            return error_response(message='不能修改管理员状态')

        user.is_active = not user.is_active
        user.save()
        status_text = '启用' if user.is_active else '禁用'
        return success_response(message=f'已{status_text}用户 {user.username}')


class AdminUserDetailView(APIView):
    """管理员 - 用户详情"""
    permission_classes = [IsAdmin]

    def get(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return error_response(message='用户不存在', code=404)

        data = UserInfoSerializer(user).data
        return success_response(data=data)