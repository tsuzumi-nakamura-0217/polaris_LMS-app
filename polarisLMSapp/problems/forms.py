from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import Choice, Problem


class ProblemForm(forms.ModelForm):
    """問題作成・編集フォーム"""

    DIFFICULTY_CHOICES = [
        ("", "---------"),
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
    ]

    difficulty = forms.TypedChoiceField(
        choices=DIFFICULTY_CHOICES,
        coerce=int,
        empty_value=None,
        required=False,
        label="難易度（1-5）",
    )

    class Meta:
        model = Problem
        fields = ["category", "problem_type", "problem", "answer", "difficulty"]

    def clean(self):
        """記述式の場合は answer を必須にする"""
        cleaned_data = super().clean()
        problem_type = cleaned_data.get("problem_type")
        answer = (cleaned_data.get("answer") or "").strip()

        if problem_type == "text" and not answer:
            self.add_error("answer", "記述式問題では正解を入力してください。")

        return cleaned_data


class BaseChoiceFormSet(BaseInlineFormSet):
    """選択式の選択肢バリデーションを提供するフォームセット"""

    def __init__(self, *args, **kwargs):
        self.problem_type = kwargs.pop("problem_type", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        if any(self.errors):
            return

        if self.problem_type != "choice":
            return

        valid_choice_count = 0
        correct_choice_count = 0

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue

            cleaned_data = form.cleaned_data
            if not cleaned_data or cleaned_data.get("DELETE"):
                continue

            choice_label = (cleaned_data.get("choice_label") or "").strip()
            choice_text = (cleaned_data.get("choice_text") or "").strip()
            if not choice_label and not choice_text:
                continue

            valid_choice_count += 1
            if cleaned_data.get("is_correct"):
                correct_choice_count += 1

        if valid_choice_count < 2:
            raise forms.ValidationError("選択式問題では選択肢を2件以上入力してください。")

        if correct_choice_count != 1:
            raise forms.ValidationError("選択式問題では正解を1件だけ選択してください。")


ChoiceFormSet = inlineformset_factory(
    Problem,
    Choice,
    formset=BaseChoiceFormSet,
    fields=["choice_label", "choice_text", "is_correct", "display_order"],
    extra=4,
    can_delete=True,
)