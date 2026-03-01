from django.contrib import admin
from .models import Subject, ProblemCategory, Problem, Choice

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_name', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('subject_name',)
    ordering = ('display_order',)


@admin.register(ProblemCategory)
class ProblemCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'grade', 'display_order', 'is_active')
    list_filter = ('subject', 'grade')


# Problem の編集画面内に選択肢を表示
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4  # 空の入力欄を4つ表示

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('problem', 'category', 'problem_type', 'difficulty', 'is_active')
    list_filter = ('category__subject', 'problem_type', 'difficulty')
    inlines = [ChoiceInline]