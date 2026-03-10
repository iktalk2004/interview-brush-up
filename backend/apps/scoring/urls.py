from django.urls import path
from .views import ScorePreviewView

urlpatterns = [
    path('preview', ScorePreviewView.as_view(), name='score_preview'),
]