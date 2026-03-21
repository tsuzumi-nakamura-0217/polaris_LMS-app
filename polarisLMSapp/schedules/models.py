from django.db import models
from django.conf import settings
from problems.models import Problem


class Status(models.Model):
    """ステータスマスター（未着手・進行中・完了）"""
    status = models.CharField(max_length=30, unique=True, verbose_name='ステータス名')
    display_order = models.IntegerField(default=0, verbose_name='表示順')

    class Meta:
        ordering = ['display_order']
        verbose_name = 'ステータス'
        verbose_name_plural = 'ステータス'

    def __str__(self):
        return self.status


class Schedule(models.Model):
    """学習スケジュール"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='生徒'
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='問題'
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        verbose_name='ステータス'
    )
    scheduled_date = models.DateField(verbose_name='予定日')
    memo = models.CharField(max_length=200, blank=True, default='', verbose_name='メモ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_date', 'created_at']
        verbose_name = 'スケジュール'
        verbose_name_plural = 'スケジュール'

    def __str__(self):
        return f'{self.student.user_name} - {self.problem} ({self.scheduled_date})'