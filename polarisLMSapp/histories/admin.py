from django.contrib import admin
from .models import History


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('student', 'problem', 'is_correct', 'level', 'duration_seconds', 'created_at')
    list_filter = ('is_correct', 'level', 'student', 'problem__category__subject')
    search_fields = ('student__user_name', 'problem__problem')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
