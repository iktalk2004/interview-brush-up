from django.urls import path
from .views import AdminStatsOverviewView

urlpatterns = [
    path('stats/overview', AdminStatsOverviewView.as_view(), name='admin_stats_overview'),
]