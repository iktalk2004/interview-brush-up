from django.urls import path
from apps.users.views import (
    RegisterView, LoginView, TokenRefreshView,
    ForgotPasswordView, ResetPasswordView,
)

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('forgot-password', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password', ResetPasswordView.as_view(), name='reset_password'),
]