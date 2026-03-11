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


# 科目-カテゴリ（単元）テーブル
class SubjectCategory(models.Model):
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
        verbose_name = '科目-カテゴリ(単元)'
        verbose_name_plural = '科目-カテゴリ(単元)'

    def __str__(self):
        return f'{self.subject.subject_name} / {self.title}（{self.grade}年）'
    

# 問題テーブル
class Problem(models.Model):
    PROBLEM_TYPE_CHOICES = [
        ('text', '記述式'),
        ('choice', '選択式'),
    ]

    category = models.ForeignKey(
        SubjectCategory,
        on_delete=models.CASCADE,
        related_name='problems',
        verbose_name='カテゴリ'
    )
    problem_type = models.CharField(
        max_length=10,
        choices=PROBLEM_TYPE_CHOICES,
        default='text',
        verbose_name='出題形式'
    )
    problem = models.CharField(max_length=500, verbose_name='問題文')
    answer = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='正解（記述式用）'
    )
    difficulty = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='難易度（1-5）'
    )
    display_order = models.IntegerField(default=0, verbose_name='表示順')
    is_active = models.BooleanField(default=True, verbose_name='有効')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'display_order']
        verbose_name = '問題'
        verbose_name_plural = '問題'

    def __str__(self):
        return f'[{self.category.title}] {self.problem[:30]}'
    

# 選択式問題の選択肢
class Choice(models.Model):
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name='問題'
    )
    choice_label = models.CharField(max_length=10, verbose_name='ラベル')  # ア、イ、ウ、エ
    choice_text = models.CharField(max_length=200, verbose_name='選択肢テキスト')
    is_correct = models.BooleanField(default=False, verbose_name='正解')
    display_order = models.IntegerField(default=0, verbose_name='表示順')

    class Meta:
        ordering = ['display_order']
        verbose_name = '選択肢'
        verbose_name_plural = '選択肢'

    def __str__(self):
        return f'{self.choice_label}: {self.choice_text}'