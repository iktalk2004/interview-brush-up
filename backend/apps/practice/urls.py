from django.urls import path
from .views import (
    QuestionHistoryView, MistakeListView, MistakeRemoveView,
    TopicListView, TopicQuestionsView,
)

urlpatterns = [
    path('history/<int:question_id>', QuestionHistoryView.as_view(), name='question_history'),
    path('mistakes', MistakeListView.as_view(), name='mistake_list'),
    path('mistakes/<int:question_id>', MistakeRemoveView.as_view(), name='mistake_remove'),
    path('topics', TopicListView.as_view(), name='topic_list'),
    path('topics/questions', TopicQuestionsView.as_view(), name='topic_questions'),
]