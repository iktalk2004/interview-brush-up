from django.urls import path
from .views import AnnouncementPublicListView

urlpatterns = [
    path('', AnnouncementPublicListView.as_view(), name='announcement_list'),
]