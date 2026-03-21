from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import Schedule, Status
from .forms import ScheduleForm
from histories.models import History


@login_required
def schedule_list(request):
    """スケジュール一覧ビュー"""
    schedules = _get_schedules_for_user(request)

    # 未完了が先に来るようにソート（完了を後ろに）
    schedules = schedules.select_related(
        'problem', 'problem__category', 'problem__category__subject', 'status', 'student'
    ).order_by('status__display_order', 'scheduled_date')

    context = {
        'schedules': schedules,
        'is_today_view': False,
        'page_title': 'スケジュール一覧',
    }
    return render(request, 'schedules/schedule_list.html', context)


@login_required
def today_schedule(request):
    """今日のスケジュールビュー"""
    today = timezone.now().date()
    schedules = _get_schedules_for_user(request).filter(scheduled_date=today)

    schedules = schedules.select_related(
        'problem', 'problem__category', 'problem__category__subject', 'status', 'student'
    ).order_by('status__display_order', 'scheduled_date')

    context = {
        'schedules': schedules,
        'is_today_view': True,
        'page_title': '今日のスケジュール',
    }
    return render(request, 'schedules/schedule_list.html', context)


def _get_schedules_for_user(request):
    """ユーザーの権限に応じたスケジュールを取得する"""
    user = request.user

    if user.user_type == 'student':
        # 生徒: 自分のスケジュールのみ
        return Schedule.objects.filter(student=user)
    else:
        # スタッフ・管理者: 指定した生徒 or 全て
        student_id = request.GET.get('student_id')
        if student_id:
            return Schedule.objects.filter(student_id=student_id)
        return Schedule.objects.all()


@login_required
def schedule_create(request):
    """スケジュール作成ビュー（スタッフ・管理者のみ）"""
    if request.user.user_type not in ('staff', 'admin'):
        raise PermissionDenied

    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.status = Status.objects.get(status='未着手')
            schedule.save()
            messages.success(request, 'スケジュールを作成しました。')
            return redirect('schedules:schedule_list')
    else:
        form = ScheduleForm()
        # 問題詳細から来た場合、問題を事前選択
        problem_id = request.GET.get('problem_id')
        if problem_id:
            form.fields['problem'].initial = problem_id

    context = {
        'form': form,
        'page_title': 'スケジュール作成',
    }
    return render(request, 'schedules/schedule_form.html', context)


@login_required
def solve_problem(request, pk):
    """スケジュールから問題を解く"""
    schedule = get_object_or_404(Schedule, pk=pk, student=request.user)
    problem = schedule.problem

    if request.method == 'GET':
        # ステータスを「進行中」に更新
        in_progress = Status.objects.get(status='進行中')
        schedule.status = in_progress
        schedule.save()

        # 解答開始時刻をセッションに保存
        request.session[f'start_time_{pk}'] = timezone.now().isoformat()

        choices = problem.choices.all() if problem.problem_type == 'choice' else None
        context = {
            'schedule': schedule,
            'problem': problem,
            'choices': choices,
        }
        return render(request, 'schedules/solve_problem.html', context)

    elif request.method == 'POST':
        # 解答を受け取る
        user_answer = request.POST.get('answer', '')
        level = int(request.POST.get('level', 3))

        # 正誤判定
        if problem.problem_type == 'text':
            is_correct = (user_answer.strip() == problem.answer.strip())
        else:
            selected_choice_id = request.POST.get('choice')
            if selected_choice_id:
                selected_choice = problem.choices.get(id=selected_choice_id)
                is_correct = selected_choice.is_correct
                user_answer = selected_choice.choice_text
            else:
                is_correct = False

        # 時間計算
        start_time_str = request.session.pop(f'start_time_{pk}', None)
        if start_time_str:
            from datetime import datetime
            started_at = datetime.fromisoformat(start_time_str)
        else:
            started_at = timezone.now()
        finished_at = timezone.now()
        duration = int((finished_at - started_at).total_seconds())

        # 履歴を保存
        History.objects.create(
            problem=problem,
            student=request.user,
            level=level,
            started_at=started_at,
            finished_at=finished_at,
            duration_seconds=duration,
            is_correct=is_correct,
        )

        # スケジュールのステータスを「完了」に更新
        completed = Status.objects.get(status='完了')
        schedule.status = completed
        schedule.save()

        # 結果画面へ
        context = {
            'schedule_pk': pk,
            'problem': problem,
            'user_answer': user_answer,
            'is_correct': is_correct,
            'level': level,
            'duration': duration,
            'correct_answer': problem.answer if problem.problem_type == 'text' else ', '.join(
                c.choice_text for c in problem.choices.filter(is_correct=True)
            ),
        }
        return render(request, 'schedules/solve_result.html', context)
