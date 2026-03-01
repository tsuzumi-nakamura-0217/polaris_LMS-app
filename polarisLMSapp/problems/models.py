from django.db import models

# 科目マスター（数学・国語・英語・理科・社会 など）
class Subject(models.Model):
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

# 問題-カテゴリ（単元）テーブル
class ProblemCategory(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name='科目'
    )
    title = models.CharField(max_length=50, verbose_name='カテゴリ名')
    grade = models.IntegerField(verbose_name='対象学年')  # 1〜12
    display_order = models.IntegerField(default=0, verbose_name='表示順')
    is_active = models.BooleanField(default=True, verbose_name='有効')

    class Meta:
        ordering = ['subject', 'grade', 'display_order']
        verbose_name = '問題-カテゴリ(単元)'
        verbose_name_plural = '問題-カテゴリ(単元)'

    def __str__(self):
        return f'{self.subject.subject_name} / {self.title}（{self.grade}年）'