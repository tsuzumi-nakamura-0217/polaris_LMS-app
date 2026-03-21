from django.contrib import admin
from .models import Status, Schedule


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
	list_display = ('status', 'display_order')
	list_editable = ('display_order',)
	search_fields = ('status',)
	ordering = ('display_order', 'id')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('student', 'problem', 'status', 'scheduled_date', 'updated_at')
    list_filter = ('status', 'scheduled_date', 'student')
    search_fields = ('student__user_name', 'problem__problem', 'memo')
    ordering = ('scheduled_date', 'student')
