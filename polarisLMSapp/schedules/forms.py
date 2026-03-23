from django import forms
from .models import Schedule
from accounts.models import User


class ScheduleForm(forms.ModelForm):
    """スケジュール作成フォーム"""

    class Meta:
        model = Schedule
        fields = ['problem', 'scheduled_date', 'memo']
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
        self.fields['problem'].widget.attrs.update({'class': 'form-input'})
