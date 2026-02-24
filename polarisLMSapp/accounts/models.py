from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

# User登録するときに呼ぶ関数
class UserManager(BaseUserManager):
    """カスタムユーザーマネージャー"""
    
    def create_user(self, user_name, password=None, **extra_fields):
        """通常ユーザーを作成"""
        if not user_name:
            raise ValueError('ユーザー名は必須です')
        
        user = self.model(user_name=user_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, user_name, password=None, **extra_fields):
        """スーパーユーザーを作成"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'administrator')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('スーパーユーザーは is_staff=True である必要があります')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('スーパーユーザーは is_superuser=True である必要があります')
        
        return self.create_user(user_name, password, **extra_fields)

# Userテーブル
class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ('student', '生徒'),
        ('guardian', '保護者'),
        ('staff', 'スタッフ'),
        ('admin', '管理者'),
    ]
    
    user_name = models.CharField('ユーザー名',max_length=50,unique=True,help_text='ログイン用ID')
    user_type = models.CharField('ユーザータイプ',max_length=20,choices=USER_TYPE_CHOICES)
    grade = models.IntegerField('学年',null=True,blank=True,help_text='生徒の場合のみ')
    is_active = models.BooleanField('有効',default=True)
    is_staff = models.BooleanField('スタッフ権限',default=False,)
    created_at = models.DateTimeField('作成日時',default=timezone.now)
    updated_at = models.DateTimeField('更新日時',auto_now=True)
    objects = UserManager()
    
    # Django管理画面で使用するフィールド
    USERNAME_FIELD = 'user_name'
    REQUIRED_FIELDS = ['user_type']
    
    class Meta:
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'
        db_table = 'user'
    
    def __str__(self):
        return f"{self.user_name} ({self.get_user_type_display()})"
    
# 保護者-生徒 テーブル
class GuardianStudent(models.Model):
    guardian = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='guardian_relations',
        limit_choices_to={'user_type': 'guardian'}
    )
    student = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_guardian',
        limit_choices_to={'user_type': 'student'}
    )
    relation = models.CharField(max_length=20, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.guardian.user_name} → {self.student.user_name}'

# スタッフ-生徒 テーブル
class StaffStudent(models.Model):
    staff = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='staff_relations',
        limit_choices_to={'user_type': 'student'}
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='student_staffs',
        limit_choices_to={'user_type': 'student'}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.staff.user_name} → {self.student.user_name}'