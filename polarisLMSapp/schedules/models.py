from django.db import models

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