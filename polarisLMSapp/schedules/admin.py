from django.contrib import admin
from .models import Status


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
	list_display = ('status', 'display_order')
	list_editable = ('display_order',)
	search_fields = ('status',)
	ordering = ('display_order', 'id')
