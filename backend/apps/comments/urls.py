from django.urls import path
from .views import CommentListView, CommentCreateView, CommentDeleteView

urlpatterns = [
    path('<int:question_id>', CommentListView.as_view(), name='comment_list'),
    path('', CommentCreateView.as_view(), name='comment_create'),
    path('<int:comment_id>/delete', CommentDeleteView.as_view(), name='comment_delete'),
]