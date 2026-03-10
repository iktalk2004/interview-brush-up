from django.urls import path
from .views import QuestionListView, QuestionDetailView

urlpatterns = [
    path('', QuestionListView.as_view(), name='question_list'),
    path('<int:question_id>', QuestionDetailView.as_view(), name='question_detail'),
]