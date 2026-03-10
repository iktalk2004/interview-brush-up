from django.urls import path
from .views import SubmitCodeView, JudgeTaskDetailView, JudgeHistoryView

urlpatterns = [
    path('submit', SubmitCodeView.as_view(), name='judge_submit'),
    path('task/<int:task_id>', JudgeTaskDetailView.as_view(), name='judge_task_detail'),
    path('history/<int:question_id>', JudgeHistoryView.as_view(), name='judge_history'),
]