from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    """ユーザー登録フォーム"""
    
    class Meta:
        model = User
        fields = ['user_name', 'user_type', 'grade', 'password1', 'password2']
        labels = {
            'user_name': 'ユーザー名（ログインID）',
            'user_type': 'ユーザータイプ',
            'grade': '学年',
        }
        help_texts = {
            'user_name': 'ログイン時に使用するIDです',
            'grade': '生徒の場合のみ入力してください',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 学年フィールドを必須から任意に変更（JavaScriptで動的に制御）
        self.fields['grade'].required = False
    
    def clean(self):
        """フォーム全体のバリデーション"""
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        grade = cleaned_data.get('grade')
        
        # 生徒の場合は学年を必須にする
        if user_type == 'student' and not grade:
            self.add_error('grade', '生徒の場合、学年の入力は必須です')
        
        return cleaned_data