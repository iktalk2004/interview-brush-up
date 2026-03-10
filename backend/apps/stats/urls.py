from django.urls import path
from .views import DashboardView, LearningTimeReportView, RankingView, PracticeHistoryView

urlpatterns = [
    path('dashboard', DashboardView.as_view(), name='dashboard'),
    path('learning-time', LearningTimeReportView.as_view(), name='learning_time'),
    path('ranking', RankingView.as_view(), name='ranking'),
    path('history', PracticeHistoryView.as_view(), name='practice_history'),
]