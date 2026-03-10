from django.urls import path
from .views import (
    AdminCategoryListView, AdminCategoryDetailView,
    AdminSubCategoryListView, AdminSubCategoryDetailView,
    AdminQuestionListView, AdminQuestionDetailView,
    AdminQuestionImportView,
)

urlpatterns = [
    # 分类管理
    path('categories', AdminCategoryListView.as_view(), name='admin_category_list'),
    path('categories/<int:category_id>', AdminCategoryDetailView.as_view(), name='admin_category_detail'),
    path('sub-categories', AdminSubCategoryListView.as_view(), name='admin_sub_category_create'),
    path('sub-categories/<int:sub_category_id>', AdminSubCategoryDetailView.as_view(), name='admin_sub_category_detail'),

    # 题目管理
    path('questions', AdminQuestionListView.as_view(), name='admin_question_list'),
    path('questions/<int:question_id>', AdminQuestionDetailView.as_view(), name='admin_question_detail'),
    path('questions/import', AdminQuestionImportView.as_view(), name='admin_question_import'),
]