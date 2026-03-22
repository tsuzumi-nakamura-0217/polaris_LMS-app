from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SignUpForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps

# カスタムデコレータ：特定のuser_typeのユーザーのみアクセス可能にする
def user_type_required(required_type):
    """指定されたuser_typeを持つユーザーのみがアクセスできるようにするデコレータ"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.user_type != required_type:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# ウェルカムページ
def welcome(request):
    """ウェルカムページのビュー"""
    return render(request, 'accounts/welcome.html')

# サインアップ
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            return redirect('accounts:welcome')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

# ログイン
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    # ようこそページのボタンによってrole振り分け
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # URLの ?role=xxx を取得してコンテキストに追加
        context['role'] = self.request.GET.get('role')
        return context

    # フォームチェック
    def form_valid(self, form):
        """認証成功後に `user_type` と渡された `role` を比較して一致しなければ拒否する"""
        user = form.get_user()
        role = self.request.POST.get('role') or self.request.GET.get('role')
        if role:
            if getattr(user, 'user_type', None) != role:
                form.add_error(None, 'このアカウントは指定されたロールでログインできません。')
                return self.form_invalid(form)
        return super().form_valid(form)
    
    # ログイン成功後のリダイレクト先をロールごとに切り替える
    def get_success_url(self):
        role = self.request.POST.get('role')
        if role == 'student':
            return reverse_lazy('accounts:student_home')  # 生徒用ページへ
        elif role == 'guardian':
            return reverse_lazy('accounts:guardian_home')   # 保護者用ページへ
        elif role == 'staff':
            return reverse_lazy('accounts:staff_home')    # スタッフ用ページへ
        elif role == 'admin':
            return reverse_lazy('accounts:admin_home')    # 管理者用ページへ

# 各ホームページビュー
from schedules.models import Schedule
from histories.models import History
from django.utils import timezone
from django.db.models import Q
from .models import GuardianStudent, StaffStudent, User

@login_required
@user_type_required('student')
def student_home(request):
    today = timezone.now().date()
    
    # 今日のスケジュール（過去の未完了 + 今日のすべて）から完了済みを除外
    today_schedules = Schedule.objects.filter(
        Q(student=request.user) & 
        (Q(scheduled_date=today) | Q(scheduled_date__lt=today, status__status__in=['未着手', '進行中']))
    ).exclude(status__status='完了').select_related('problem', 'status').order_by('scheduled_date', 'status__display_order')

    # 最近の学習履歴
    recent_histories = History.objects.filter(
        student=request.user
    ).select_related('problem').order_by('-created_at')[:5]

    # 総問題回答数
    total_answers = History.objects.filter(student=request.user).count()

    context = {
        'today': today,
        'today_schedules': today_schedules,
        'recent_histories': recent_histories,
        'total_answers': total_answers,
        # デモ用のダミーデータ（必要に応じて後で実際のロジックに置き換え）
        'total_login_days': 10,
        'consecutive_login_days': 3,
        'tasks_count': today_schedules.exclude(status__status='完了').count(),
    }
    return render(request, 'accounts/student_home.html', context)

@login_required
def student_detail_dashboard(request, student_id):
    target_student = get_object_or_404(User, pk=student_id, user_type='student')
    
    user = request.user
    if user.user_type == 'student':
        if user.id != target_student.id:
            raise PermissionDenied
    elif user.user_type == 'guardian':
        if not GuardianStudent.objects.filter(guardian=user, student=target_student).exists():
            raise PermissionDenied
    elif user.user_type == 'staff':
        if not StaffStudent.objects.filter(staff=user, student=target_student, is_active=True).exists():
            raise PermissionDenied
            
    today = timezone.now().date()
    
    today_schedules = Schedule.objects.filter(
        Q(student=target_student) & 
        (Q(scheduled_date=today) | Q(scheduled_date__lt=today, status__status__in=['未着手', '進行中']))
    ).exclude(status__status='完了').select_related('problem', 'status').order_by('scheduled_date', 'status__display_order')

    recent_histories = History.objects.filter(
        student=target_student
    ).select_related('problem').order_by('-created_at')[:5]

    total_answers = History.objects.filter(student=target_student).count()

    context = {
        'target_student': target_student,
        'today': today,
        'today_schedules': today_schedules,
        'recent_histories': recent_histories,
        'total_answers': total_answers,
        'total_login_days': 10,
        'consecutive_login_days': 3,
        'tasks_count': today_schedules.exclude(status__status='完了').count(),
    }
    return render(request, 'accounts/student_detail_dashboard.html', context)

@login_required
@user_type_required('guardian')
def guardian_home(request):
    today = timezone.now().date()
    students = [rel.student for rel in GuardianStudent.objects.filter(guardian=request.user).select_related('student')]
    
    student_data = []
    for student in students:
        tasks_count = Schedule.objects.filter(
            Q(student=student) & 
            (Q(scheduled_date=today) | Q(scheduled_date__lt=today, status__status__in=['未着手', '進行中']))
        ).exclude(status__status='完了').count()

        student_data.append({
            'student': student,
            'tasks_count': tasks_count,
            'total_answers': History.objects.filter(student=student).count(),
        })

    context = {'student_data': student_data}
    return render(request, 'accounts/guardian_home.html', context)

@login_required     
@user_type_required('staff')
def staff_home(request):
    today = timezone.now().date()
    students = [rel.student for rel in StaffStudent.objects.filter(staff=request.user, is_active=True).select_related('student')]
    
    student_data = []
    for student in students:
        tasks_count = Schedule.objects.filter(
            Q(student=student) & 
            (Q(scheduled_date=today) | Q(scheduled_date__lt=today, status__status__in=['未着手', '進行中']))
        ).exclude(status__status='完了').count()

        student_data.append({
            'student': student,
            'tasks_count': tasks_count,
            'total_answers': History.objects.filter(student=student).count(),
        })

    context = {'student_data': student_data}
    return render(request, 'accounts/staff_home.html', context)

@login_required
@user_type_required('staff')
def staff_select_student(request, student_id):
    target_student = get_object_or_404(User, pk=student_id, user_type='student')
    
    if not StaffStudent.objects.filter(staff=request.user, student=target_student, is_active=True).exists():
        raise PermissionDenied
        
    request.session['selected_student_id'] = student_id
    
    return redirect('accounts:student_detail_dashboard', student_id=student_id)

@login_required
@user_type_required('admin')
def admin_home(request):
    today = timezone.now().date()
    
    total_students = User.objects.filter(user_type='student', is_active=True).count()
    total_staff = User.objects.filter(user_type__in=['staff', 'guardian', 'admin'], is_active=True).count()
    total_answers_today = History.objects.filter(created_at__date=today).count()
    total_active_tasks = Schedule.objects.filter(status__status__in=['未着手', '進行中']).count()
    
    recent_histories = History.objects.select_related('student', 'problem').order_by('-created_at')[:10]

    all_students = User.objects.filter(user_type='student', is_active=True).order_by('-created_at')

    context = {
        'total_students': total_students,
        'total_staff': total_staff,
        'total_answers_today': total_answers_today,
        'total_active_tasks': total_active_tasks,
        'recent_histories': recent_histories,
        'all_students': all_students,
    }
    return render(request, 'accounts/admin_home.html', context)

# ログアウト
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:welcome')
    template_name = 'accounts/base.html'