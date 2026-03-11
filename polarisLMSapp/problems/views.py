from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Problem, Subject, SubjectCategory

@login_required
def problem_list(request):
    problems = Problem.objects.filter(is_active=True).select_related('category', 'category__subject')

    # フィルタリング
    subject_id = request.GET.get('subject')
    grade = request.GET.get('grade')

    if subject_id:
        problems = problems.filter(category__subject_id=subject_id)
    
    if grade:
        problems = problems.filter(category__grade=grade)

    context = {
        'problems': problems,
        'subjects': Subject.objects.all(),
        'selected_subject': int(subject_id) if subject_id else None,
        'selected_grade': int(grade) if grade else None,
    }
    return render(request, 'problems/problem_list.html', context)