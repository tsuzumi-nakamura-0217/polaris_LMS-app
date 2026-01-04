from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """カスタムユーザーの管理画面設定"""
    
    list_display = ['user_name', 'user_type', 'grade', 'is_active', 'is_staff']
    list_filter = ['user_type', 'is_active', 'is_staff', 'grade']
    search_fields = ['user_name']
    ordering = ['user_name']
    
    fieldsets = (
        (None, {'fields': ('user_name', 'password')}),
        ('個人情報', {'fields': ('user_type', 'grade')}),
        ('権限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('重要な日付', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_name', 'user_type', 'grade', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']
