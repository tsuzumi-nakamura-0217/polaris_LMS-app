from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import Schedule, Status
from .forms import ScheduleForm
from histories.models import History
import calendar
from datetime import date, timedelta, datetime
from django.db.models import F
from accounts.models import User
from problems.models import Problem, Subject, SubjectCategory


@login_required
def schedule_list(request):
    """スケジュール一覧ビュー"""
    schedules = _get_schedules_for_user(request)

    filter_date_str = request.GET.get('date')
    filter_date = None
    if filter_date_str:
        try:
            filter_date = datetime.strptime(filter_date_str, '%Y-%m-%d').date()
            schedules = schedules.filter(scheduled_date=filter_date)
        except ValueError:
            pass

    # 未完了が先に来るようにソート（完了を後ろに）
    schedules = schedules.select_related(
        'problem', 'problem__category', 'problem__category__subject', 'status', 'student'
    ).order_by('status__display_order', 'scheduled_date')

    if filter_date:
        page_title = f'{filter_date.strftime("%m/%d")}のスケジュール'
    else:
        page_title = 'スケジュール一覧'

    context = {
        'schedules': schedules,
        'is_today_view': False,
        'page_title': page_title,
        'filter_date': filter_date_str,
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
        student_id = request.GET.get('student_id') or request.session.get('selected_student_id')
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
            student_id = request.session.get('selected_student_id')
            if not student_id:
                messages.error(request, '生徒が選択されていません。')
                return redirect('schedules:schedule_list')
            schedule.student_id = student_id
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

        # 次の未完了のスケジュールを探す（今日 または 過去の未完了）
        from django.db.models import Q
        today_date = timezone.now().date()
        next_schedule = Schedule.objects.filter(
            Q(student=request.user) & 
            (Q(scheduled_date=today_date) | Q(scheduled_date__lt=today_date, status__status__in=['未着手', '進行中']))
        ).exclude(id=schedule.id).exclude(status__status='完了').order_by('scheduled_date', 'status__display_order').first()

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
            'next_schedule': next_schedule,
        }
        return render(request, 'schedules/solve_result.html', context)


@login_required
def calendar_view(request, year=None, month=None):
    """月別カレンダービュー"""
    today = timezone.now().date()
    
    if year is None or month is None:
        year = today.year
        month = today.month

    start_date = date(year, month, 1)
    if month == 12:
        next_month_start = date(year + 1, 1, 1)
    else:
        next_month_start = date(year, month + 1, 1)
        
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdatescalendar(year, month)
    
    cal_start_date = month_days[0][0]
    cal_end_date = month_days[-1][-1]
    
    schedules = _get_schedules_for_user(request).filter(
        scheduled_date__gte=cal_start_date,
        scheduled_date__lte=cal_end_date
    )

    schedules_by_date = {}
    for schedule in schedules:
        d = schedule.scheduled_date
        if d not in schedules_by_date:
            schedules_by_date[d] = []
        schedules_by_date[d].append(schedule)

    month_data = []
    for week in month_days:
        week_data = []
        for d in week:
            day_schedules = schedules_by_date.get(d, [])
            
            display_statuses = []
            if day_schedules:
                counts = {}
                for sch in day_schedules:
                    status_name = sch.status.status
                    counts[status_name] = counts.get(status_name, 0) + 1
                
                for status_name, css_class in [('未着手', 'status-not-started'), ('進行中', 'status-in-progress'), ('完了', 'status-completed')]:
                    if counts.get(status_name, 0) > 0:
                        if d < today and status_name in ['未着手', '進行中']:
                            css_class = 'status-overdue'
                        display_statuses.append({'name': status_name, 'count': counts[status_name], 'css_class': css_class})
                
                for status_name, count in counts.items():
                    if status_name not in ['未着手', '進行中', '完了']:
                        display_statuses.append({'name': status_name, 'count': count, 'css_class': 'status-other'})

            week_data.append({
                'date': d,
                'day_number': d.day,
                'is_current_month': d.month == month,
                'is_today': d == today,
                'schedules_count': len(day_schedules),
                'display_statuses': display_statuses,
                'is_past': d < today
            })
        month_data.append(week_data)

    prev_month_date = start_date - timedelta(days=1)
    
    context = {
        'page_title': 'カレンダー',
        'year': year,
        'month': month,
        'month_data': month_data,
        'today': today,
        'prev_year': prev_month_date.year,
        'prev_month': prev_month_date.month,
        'next_year': next_month_start.year,
        'next_month': next_month_start.month,
    }
    return render(request, 'schedules/calendar.html', context)


@login_required
def schedule_batch_create(request):
    """スケジュール一括作成・DB表示ビュー（スタッフ・管理者のみ）"""
    if request.user.user_type not in ('staff', 'admin'):
        raise PermissionDenied

    # フィルタ用のデータ
    subjects = Subject.objects.filter(is_active=True).order_by('display_order')
    # 選択用の生徒リスト
    students = User.objects.filter(user_type='student', is_active=True).order_by('user_name')

    if request.method == 'POST':
        student_id = request.session.get('selected_student_id')
        if not student_id:
            messages.error(request, '生徒が選択されていません。')
            return redirect('schedules:schedule_batch_create')

        student = get_object_or_404(User, id=student_id)
        not_started = Status.objects.get(status='未着手')
        created_count = 0

        for key, value in request.POST.items():
            if key.startswith('scheduled_date_') and value:
                # value is a date string like '2023-10-01'
                problem_id = key.replace('scheduled_date_', '')
                try:
                    problem = Problem.objects.get(id=problem_id, is_active=True)
                    # Create schedule
                    Schedule.objects.create(
                        student=student,
                        problem=problem,
                        status=not_started,
                        scheduled_date=value
                    )
                    created_count += 1
                except (Problem.DoesNotExist, ValueError):
                    pass

        if created_count > 0:
            messages.success(request, f'{created_count}件のスケジュールを作成しました。')
            return redirect('schedules:schedule_list')
        else:
            messages.warning(request, '作成されたスケジュールはありませんでした（日付が未入力など）。')
            return redirect('schedules:schedule_batch_create')

    # GET リクエスト（フィルタ処理）
    subject_id = request.GET.get('subject_id', '')
    grade = request.GET.get('grade', '')
    category_id = request.GET.get('category_id', '')
    sort_by = request.GET.get('sort_by', 'default')

    problems = Problem.objects.filter(is_active=True).select_related(
        'category', 'category__subject'
    )

    if subject_id:
        problems = problems.filter(category__subject_id=subject_id)
    if grade:
        problems = problems.filter(category__grade=grade)
    if category_id:
        problems = problems.filter(category_id=category_id)

    # 並べ替え処理
    if sort_by == 'difficulty_asc':
        problems = problems.order_by(F('difficulty').asc(nulls_last=True), 'category__subject__display_order', 'category__grade', 'category__display_order', 'display_order')
    elif sort_by == 'difficulty_desc':
        problems = problems.order_by(F('difficulty').desc(nulls_last=True), 'category__subject__display_order', 'category__grade', 'category__display_order', 'display_order')
    elif sort_by == 'category_asc':
        problems = problems.order_by('category__title', 'category__grade', 'display_order')
    else:
        # デフォルト
        problems = problems.order_by('category__subject__display_order', 'category__grade', 'category__display_order', 'display_order')

    # 学年の重複のないリスト（フィルタ用オプションとして）
    grades = Problem.objects.filter(is_active=True).values_list('category__grade', flat=True).distinct().order_by('category__grade')
    
    # カテゴリのリスト（フィルタ用オプションとして）
    categories = SubjectCategory.objects.filter(is_active=True).select_related('subject').order_by('subject__display_order', 'grade', 'display_order')

    # 生徒が選択されていれば、直近の成績と理解度を取得
    student_id = request.session.get('selected_student_id')
    if student_id:
        from histories.models import History
        from django.db.models import Subquery, OuterRef
        
        latest_history = History.objects.filter(
            problem=OuterRef('pk'),
            student_id=student_id
        ).order_by('-created_at')
        
        problems = problems.annotate(
            recent_is_correct=Subquery(latest_history.values('is_correct')[:1]),
            recent_level=Subquery(latest_history.values('level')[:1])
        )

    context = {
        'page_title': 'スケジュール一括作成',
        'problems': problems,
        'subjects': subjects,
        'selected_subject': int(subject_id) if subject_id.isdigit() else None,
        'grades': grades,
        'selected_grade': int(grade) if grade.isdigit() else None,
        'categories': categories,
        'selected_category': int(category_id) if category_id.isdigit() else None,
        'selected_sort': sort_by,
    }
    return render(request, 'schedules/schedule_batch_create.html', context)
