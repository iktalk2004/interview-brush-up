from django.contrib import admin
from .models import JudgeTask

@admin.register(JudgeTask)
class JudgeTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'question', 'language', 'status', 'passed_count', 'total_count', 'created_at']
    list_filter = ['status', 'language']