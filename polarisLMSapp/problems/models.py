from django.db import models

class Subject(models.Model):
    """科目マスター（数学・国語・英語・理科・社会 など）"""
    subject_name = models.CharField(max_length=50, unique=True, verbose_name='科目名')
    display_order = models.IntegerField(default=0, verbose_name='表示順')
    is_active = models.BooleanField(default=True, verbose_name='有効')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order']
        verbose_name = '科目'
        verbose_name_plural = '科目'

    def __str__(self):
        return self.subject_name
