from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import Schedule, Status
from .forms import ScheduleForm


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
