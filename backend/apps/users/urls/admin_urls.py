from django.urls import path
from apps.users.views import (
    AdminUserListView, AdminUserStatusView, AdminUserDetailView,
)

urlpatterns = [
    path('users', AdminUserListView.as_view(), name='admin_user_list'),
    path('users/<int:user_id>/status', AdminUserStatusView.as_view(), name='admin_user_status'),
    path('users/<int:user_id>', AdminUserDetailView.as_view(), name='admin_user_detail'),
]