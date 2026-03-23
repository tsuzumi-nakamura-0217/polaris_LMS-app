from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import History


@login_required
def history_list(request):
    """学習履歴一覧ビュー"""
    user = request.user

    if user.user_type == 'student':
        # 生徒: 自分の履歴のみ
        histories = History.objects.filter(student=user)
    elif user.user_type == 'guardian':
        # 保護者: 担当生徒の履歴
        from accounts.models import GuardianStudent
        student_ids = GuardianStudent.objects.filter(
            guardian=user
        ).values_list('student_id', flat=True)
        histories = History.objects.filter(student_id__in=student_ids)
    elif user.user_type == 'staff':
        # スタッフ: 選択中の生徒または担当生徒の履歴
        from accounts.models import StaffStudent
        selected_student_id = request.session.get('selected_student_id')
        if selected_student_id:
            # 選択中の生徒が自分の担当か確認
            if StaffStudent.objects.filter(staff=user, student_id=selected_student_id, is_active=True).exists():
                histories = History.objects.filter(student_id=selected_student_id)
            else:
                histories = History.objects.none()
        else:
            student_ids = StaffStudent.objects.filter(
                staff=user, is_active=True
            ).values_list('student_id', flat=True)
            histories = History.objects.filter(student_id__in=student_ids)
    else:
        # 管理者: 全員の履歴
        histories = History.objects.all()

    histories = histories.select_related(
        'problem', 'problem__category', 'problem__category__subject', 'student'
    ).order_by('-created_at')

    context = {
        'histories': histories,
    }
    return render(request, 'histories/history_list.html', context)
