from django.urls import path
from .views import HomeRecommendView, DailyRecommendView

urlpatterns = [
    path('home', HomeRecommendView.as_view(), name='recommend_home'),
    path('daily', DailyRecommendView.as_view(), name='recommend_daily'),
]