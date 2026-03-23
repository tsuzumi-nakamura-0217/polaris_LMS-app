from django.db import models
from django.conf import settings
from problems.models import Problem

class History(models.Model):
    """学習履歴"""
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='histories',
        verbose_name='問題'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='histories',
        verbose_name='生徒'
    )
    level = models.IntegerField(verbose_name='理解度（1-5）')
    started_at = models.DateTimeField(verbose_name='解答開始時刻')
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='解答終了時刻')
    duration_seconds = models.IntegerField(null=True, blank=True, verbose_name='所要時間（秒）')
    is_correct = models.BooleanField(null=True, blank=True, verbose_name='正解したか')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '学習履歴'
        verbose_name_plural = '学習履歴'

    def __str__(self):
        result = '○' if self.is_correct else '×'
        return f'{self.student.user_name} - {self.problem} [{result}]'

    def save(self, *args, **kwargs):
        """保存時に所要時間を自動計算する"""
        if self.started_at and self.finished_at:
            delta = self.finished_at - self.started_at
            self.duration_seconds = int(delta.total_seconds())
        super().save(*args, **kwargs)