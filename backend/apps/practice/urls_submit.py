from django.urls import path
from .views import SubmitTextAnswerView

urlpatterns = [
    path('text', SubmitTextAnswerView.as_view(), name='submit_text'),
]