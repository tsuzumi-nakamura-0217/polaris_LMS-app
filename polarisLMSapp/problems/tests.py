from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from .models import Subject, SubjectCategory, Problem, Choice


class ProblemViewsTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			user_name='student01',
			password='password123',
			user_type='student',
		)
		self.client.login(user_name='student01', password='password123')

		subject = Subject.objects.create(subject_name='英語', display_order=1)
		category = SubjectCategory.objects.create(
			subject=subject,
			title='三単現',
			grade=1,
			display_order=1,
			is_active=True,
		)

		self.choice_problem = Problem.objects.create(
			category=category,
			problem_type='choice',
			problem='He ( ) to school every day.',
			answer='',
			difficulty=2,
			display_order=1,
			is_active=True,
		)
		Choice.objects.create(
			problem=self.choice_problem,
			choice_label='ア',
			choice_text='go',
			is_correct=False,
			display_order=1,
		)
		Choice.objects.create(
			problem=self.choice_problem,
			choice_label='イ',
			choice_text='goes',
			is_correct=True,
			display_order=2,
		)

		self.text_problem = Problem.objects.create(
			category=category,
			problem_type='text',
			problem='三単現のsをつける条件を説明しなさい。',
			answer='主語が三人称単数、時制が現在のとき動詞にsをつける。',
			difficulty=3,
			display_order=2,
			is_active=True,
		)

	def test_problem_list_contains_detail_link(self):
		response = self.client.get(reverse('problems:problem_list'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, reverse('problems:problem_detail', args=[self.choice_problem.pk]))

	def test_problem_detail_view_renders_choice_problem(self):
		response = self.client.get(reverse('problems:problem_detail', args=[self.choice_problem.pk]))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'He ( ) to school every day.')
		self.assertContains(response, '解答確認')

	def test_problem_answer_view_renders_correct_choice(self):
		response = self.client.get(reverse('problems:problem_answer', args=[self.choice_problem.pk]))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '正解')
		self.assertContains(response, 'イ')
		self.assertContains(response, 'goes')

	def test_problem_answer_view_renders_text_answer(self):
		response = self.client.get(reverse('problems:problem_answer', args=[self.text_problem.pk]))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.text_problem.answer)
