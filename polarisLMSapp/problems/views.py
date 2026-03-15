from django.shortcuts import render, get_object_or_404
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

@login_required
def problem_detail(request, pk):
    """問題詳細画面"""
    problem = get_object_or_404(
        Problem.objects.select_related('category', 'category__subject'),
        pk=pk,
        is_active=True,
    )
    choices = problem.choices.all() if problem.problem_type == 'choice' else None

    context = {
        'problem': problem,
        'choices': choices,
    }
    return render(request, 'problems/problem_detail.html', context)


@login_required
def problem_answer(request, pk):
    """解答確認画面"""
    problem = get_object_or_404(
        Problem.objects.select_related('category', 'category__subject'),
        pk=pk,
        is_active=True,
    )
    correct_choices = problem.choices.filter(is_correct=True) if problem.problem_type == 'choice' else None

    context = {
        'problem': problem,
        'correct_choices': correct_choices,
    }
    return render(request, 'problems/problem_answer.html', context)