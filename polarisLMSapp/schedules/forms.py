from django import forms
from .models import Schedule
from accounts.models import User


class ScheduleForm(forms.ModelForm):
    """スケジュール作成フォーム"""

    class Meta:
        model = Schedule
        fields = ['student', 'problem', 'scheduled_date', 'memo']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input',
            }),
            'memo': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'メモ（任意）',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 生徒のみ選択できるようにする
        self.fields['student'].queryset = User.objects.filter(
            user_type='student', is_active=True
        )
        self.fields['student'].widget.attrs.update({'class': 'form-input'})
        self.fields['problem'].widget.attrs.update({'class': 'form-input'})
