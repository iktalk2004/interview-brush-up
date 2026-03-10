from django.urls import path
from .views import AdminAnnouncementListView, AdminAnnouncementDetailView

urlpatterns = [
    path('announcements', AdminAnnouncementListView.as_view(), name='admin_announcement_list'),
    path('announcements/<int:announcement_id>', AdminAnnouncementDetailView.as_view(), name='admin_announcement_detail'),
]