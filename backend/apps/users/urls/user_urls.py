from django.urls import path
from apps.users.views import (
    UserProfileView, ChangePasswordView, AvatarUploadView,
)

urlpatterns = [
    path('profile', UserProfileView.as_view(), name='user_profile'),
    path('change-password', ChangePasswordView.as_view(), name='change_password'),
    path('avatar', AvatarUploadView.as_view(), name='avatar_upload'),
]