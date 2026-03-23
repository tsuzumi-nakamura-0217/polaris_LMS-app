from functools import wraps

from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProblemForm, ChoiceFormSet
from .models import Problem, Subject, SubjectCategory


def admin_required(view_func):
    """adminユーザーのみアクセスを許可するデコレータ"""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if getattr(request.user, "user_type", None) != "admin":
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper

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


@login_required
@admin_required
def problem_create(request):
    """問題作成画面"""
    problem_instance = Problem()

    if request.method == "POST":
        form = ProblemForm(request.POST)
        posted_problem_type = request.POST.get("problem_type")
        formset = ChoiceFormSet(
            request.POST,
            instance=problem_instance,
            prefix="choices",
            problem_type=posted_problem_type,
        )

        if form.is_valid():
            problem = form.save(commit=False)

            if problem.problem_type == "choice":
                if formset.is_valid():
                    problem.save()
                    formset.instance = problem
                    formset.save()
                    messages.success(request, "問題を作成しました。")
                    return redirect("problems:problem_detail", pk=problem.pk)
            else:
                problem.save()
                messages.success(request, "問題を作成しました。")
                return redirect("problems:problem_detail", pk=problem.pk)
    else:
        form = ProblemForm()
        formset = ChoiceFormSet(
            instance=problem_instance,
            prefix="choices",
            problem_type="text",
        )

    context = {
        "form": form,
        "formset": formset,
        "is_edit": False,
    }
    return render(request, "problems/problem_form.html", context)


@login_required
@admin_required
def problem_edit(request, pk):
    """問題編集画面"""
    problem = get_object_or_404(Problem, pk=pk)

    if request.method == "POST":
        form = ProblemForm(request.POST, instance=problem)
        posted_problem_type = request.POST.get("problem_type")
        formset = ChoiceFormSet(
            request.POST,
            instance=problem,
            prefix="choices",
            problem_type=posted_problem_type,
        )

        if form.is_valid():
            updated_problem = form.save(commit=False)

            if updated_problem.problem_type == "choice":
                if formset.is_valid():
                    updated_problem.save()
                    formset.save()
                    messages.success(request, "問題を更新しました。")
                    return redirect("problems:problem_detail", pk=updated_problem.pk)
            else:
                updated_problem.save()
                updated_problem.choices.all().delete()
                messages.success(request, "問題を更新しました。")
                return redirect("problems:problem_detail", pk=updated_problem.pk)
    else:
        form = ProblemForm(instance=problem)
        formset = ChoiceFormSet(
            instance=problem,
            prefix="choices",
            problem_type=problem.problem_type,
        )

    context = {
        "form": form,
        "formset": formset,
        "is_edit": True,
        "problem": problem,
    }
    return render(request, "problems/problem_form.html", context)