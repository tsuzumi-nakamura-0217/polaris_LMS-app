from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SignUpForm
from django.shortcuts import render, redirect
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
@login_required
@user_type_required('student')
def student_home(request):
    return render(request, 'accounts/student_home.html')

@login_required
@user_type_required('guardian')
def guardian_home(request):
    return render(request, 'accounts/guardian_home.html')

@login_required     
@user_type_required('staff')
def staff_home(request):
    return render(request, 'accounts/staff_home.html')

@login_required
@user_type_required('admin')
def admin_home(request):
    return render(request, 'accounts/admin_home.html')

