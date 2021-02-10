from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.authtoken.models import Token
from django.utils import timezone
from quiz.models import QuestionTypes, Quiz, UserQuiz
from quiz.views import QuizView
from core.models import ChallengeRepo, Concept, PyGymUser
from code_challenge.models import CodeChallenge


class UserQuizTestCase(TestCase):
    def test_duration_for_quiz_about_to_end(self):
        quiz = Quiz.objects.create(title='Quiz', duration=20, deadline=timezone.now() + timezone.timedelta(minutes=5))
        user = PyGymUser.objects.create_user(username='user', password='1234')
        user_extra_percent = PyGymUser.objects.create_user(username='user_percent', password='1234', additional_quiz_time_percent=0.5, additional_quiz_time_absolute=1)
        user_extra_absolute = PyGymUser.objects.create_user(username='user_absolute', password='1234', additional_quiz_time_percent=0.1, additional_quiz_time_absolute=5)

        user_quiz = UserQuiz.objects.create(quiz=quiz, user=user)
        self.assertEqual(user_quiz.remaining_seconds, 5 * 60)

        user_quiz = UserQuiz.objects.create(quiz=quiz, user=user_extra_percent)
        self.assertEqual(user_quiz.remaining_seconds, 15 * 60)

        user_quiz = UserQuiz.objects.create(quiz=quiz, user=user_extra_absolute)
        self.assertEqual(user_quiz.remaining_seconds, 10 * 60)

    def test_duration_for_quiz_far_from_ending(self):
        quiz = Quiz.objects.create(title='Quiz', duration=10, deadline=timezone.now() + timezone.timedelta(minutes=30))
        user = PyGymUser.objects.create_user(username='user', password='1234')
        user_extra_percent = PyGymUser.objects.create_user(username='user_percent', password='1234', additional_quiz_time_percent=0.5, additional_quiz_time_absolute=1)
        user_extra_absolute = PyGymUser.objects.create_user(username='user_absolute', password='1234', additional_quiz_time_percent=0.1, additional_quiz_time_absolute=10)

        user_quiz = UserQuiz.objects.create(quiz=quiz, user=user)
        self.assertEqual(user_quiz.remaining_seconds, 10 * 60)

        user_quiz = UserQuiz.objects.create(quiz=quiz, user=user_extra_percent)
        self.assertEqual(user_quiz.remaining_seconds, 15 * 60)

        user_quiz = UserQuiz.objects.create(quiz=quiz, user=user_extra_absolute)
        self.assertEqual(user_quiz.remaining_seconds, 20 * 60)

    def test_duration_for_ended_quiz(self):
        quiz = Quiz.objects.create(title='Quiz', duration=10, deadline=timezone.now() - timezone.timedelta(minutes=50))
        user = PyGymUser.objects.create_user(username='user', password='1234')
        user_extra_percent = PyGymUser.objects.create_user(username='user_percent', password='1234', additional_quiz_time_percent=0.5, additional_quiz_time_absolute=1)
        user_extra_absolute = PyGymUser.objects.create_user(username='user_absolute', password='1234', additional_quiz_time_percent=0.1, additional_quiz_time_absolute=10)

        user_quiz = UserQuiz.objects.create(quiz=quiz, user=user)
        self.assertEqual(user_quiz.remaining_seconds, -50 * 60)

        user_quiz = UserQuiz.objects.create(quiz=quiz, user=user_extra_percent)
        self.assertEqual(user_quiz.remaining_seconds, -45 * 60)

        user_quiz = UserQuiz.objects.create(quiz=quiz, user=user_extra_absolute)
        self.assertEqual(user_quiz.remaining_seconds, -40 * 60)


class StartQuizTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = PyGymUser.objects.create_user(username='user', password='1234')
        self.token = Token.objects.create(user=self.user)

    def test_unauthorized(self):
        request = self.factory.post('/api/quiz/invalidquiz/', {'action': 'start'})
        response = QuizView.as_view()(request, 'invalidquiz')
        self.assertEqual(403, response.status_code)

    def test_invalid_quiz(self):
        request = self.factory.post('/api/quiz/invalidquiz/', {'action': 'start'})
        force_authenticate(request, user=self.user, token=self.token)
        response = QuizView.as_view()(request, 'invalidquiz')
        self.assertEqual(404, response.status_code)

    def test_start_quiz(self):
        quiz = Quiz.objects.create(title='Quiz', duration=20, deadline=timezone.now() + timezone.timedelta(minutes=50))
        request = self.factory.post(f'/api/quiz/{quiz.slug}/', {'action': 'start'})
        force_authenticate(request, user=self.user, token=self.token)
        response = QuizView.as_view()(request, quiz.slug)
        self.assertEqual(200, response.status_code)
        self.assertEqual(20 * 60, response.data['remaining_seconds'])
        self.assertFalse(response.data['submitted'])
        self.assertIsNone(response.data['submission_time'])

    def test_start_quiz_that_was_already_started(self):
        quiz = Quiz.objects.create(title='Quiz', duration=20, deadline=timezone.now() + timezone.timedelta(minutes=40))
        user_quiz = UserQuiz.objects.create(quiz=quiz, user=self.user)
        user_quiz.start_time = timezone.now() - timezone.timedelta(minutes=5)
        user_quiz.save()

        request = self.factory.post(f'/api/quiz/{quiz.slug}/', {'action': 'start'})
        force_authenticate(request, user=self.user, token=self.token)
        response = QuizView.as_view()(request, quiz.slug)
        self.assertEqual(200, response.status_code)
        self.assertEqual(15 * 60, response.data['remaining_seconds'])
        self.assertFalse(response.data['submitted'])
        self.assertIsNone(response.data['submission_time'])

    def test_start_quiz_that_was_already_submitted(self):
        quiz = Quiz.objects.create(title='Quiz', duration=20, deadline=timezone.now() + timezone.timedelta(minutes=40))
        user_quiz = UserQuiz.objects.create(quiz=quiz, user=self.user)
        user_quiz.start_time = timezone.now() - timezone.timedelta(minutes=5)
        user_quiz.submitted = True
        user_quiz.save()

        request = self.factory.post(f'/api/quiz/{quiz.slug}/', {'action': 'start'})
        force_authenticate(request, user=self.user, token=self.token)
        response = QuizView.as_view()(request, quiz.slug)
        self.assertEqual(200, response.status_code)
        self.assertEqual(15 * 60, response.data['remaining_seconds'])
        self.assertFalse(response.data['submitted'])
        self.assertIsNone(response.data['submission_time'])

    def test_cant_start_quiz_that_was_already_submitted_and_duration_exceeded(self):
        quiz = Quiz.objects.create(title='Quiz', duration=20, deadline=timezone.now() + timezone.timedelta(minutes=40))
        user_quiz = UserQuiz.objects.create(quiz=quiz, user=self.user)
        user_quiz.start_time = timezone.now() - timezone.timedelta(minutes=30)
        user_quiz.submitted = True
        user_quiz.save()

        request = self.factory.post(f'/api/quiz/{quiz.slug}/', {'action': 'start'})
        force_authenticate(request, user=self.user, token=self.token)
        response = QuizView.as_view()(request, quiz.slug)
        self.assertEqual(200, response.status_code)
        self.assertEqual(-10 * 60, response.data['remaining_seconds'])
        self.assertTrue(response.data['submitted'])
        self.assertIsNotNone(response.data['submission_time'])

    def test_cant_start_quiz_with_exceeded_duration(self):
        quiz = Quiz.objects.create(title='Quiz', duration=20, deadline=timezone.now() + timezone.timedelta(minutes=40))
        user_quiz = UserQuiz.objects.create(quiz=quiz, user=self.user)
        user_quiz.start_time = timezone.now() - timezone.timedelta(minutes=30)
        user_quiz.save()

        request = self.factory.post(f'/api/quiz/{quiz.slug}/', {'action': 'start'})
        force_authenticate(request, user=self.user, token=self.token)
        response = QuizView.as_view()(request, quiz.slug)
        self.assertEqual(200, response.status_code)
        self.assertEqual(-10 * 60, response.data['remaining_seconds'])
        self.assertTrue(response.data['submitted'])
        self.assertIsNotNone(response.data['submission_time'])

    def test_start_quiz_with_all_challenges(self):
        quiz = Quiz.objects.create(title='Quiz', question_type=QuestionTypes.ALL, duration=20, deadline=timezone.now() + timezone.timedelta(minutes=40))
        repo = ChallengeRepo.objects.create()
        concept = Concept.objects.create(name='Function', slug='function', order=1)
        challenges = [
            CodeChallenge.objects.create(
                title=f'Challenge {i}',
                slug=f'challenge-{i}',
                repo=repo,
                concept=concept,
                question=f'Question for challenge {i}',
            ) for i in range(10)
        ]
        quiz.challenges.set(challenges)

        request = self.factory.post(f'/api/quiz/{quiz.slug}/', {'action': 'start'})
        force_authenticate(request, user=self.user, token=self.token)
        response = QuizView.as_view()(request, quiz.slug)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(challenges), len(response.data['challenges']))
        slugs = [c['slug'] for c in response.data['challenges']]
        for challenge in challenges:
            self.assertIn(challenge.slug, slugs)

    def test_start_quiz_with_random_challenge(self):
        quiz = Quiz.objects.create(title='Quiz', question_type=QuestionTypes.RANDOM, duration=20, deadline=timezone.now() + timezone.timedelta(minutes=40))
        repo = ChallengeRepo.objects.create()
        concept = Concept.objects.create(name='Function', slug='function', order=1)
        challenges = [
            CodeChallenge.objects.create(
                title=f'Challenge {i}',
                slug=f'challenge-{i}',
                repo=repo,
                concept=concept,
                question=f'Question for challenge {i}',
            ) for i in range(10)
        ]
        quiz.challenges.set(challenges)

        request = self.factory.post(f'/api/quiz/{quiz.slug}/', {'action': 'start'})
        force_authenticate(request, user=self.user, token=self.token)
        response = QuizView.as_view()(request, quiz.slug)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.data['challenges']))
        slugs = [c['slug'] for c in response.data['challenges']]
        contained_slugs = [challenge.slug in slugs for challenge in challenges]
        self.assertEqual(1, sum(contained_slugs))

    def test_submit_quiz_that_was_not_started(self):
        quiz = Quiz.objects.create(title='Quiz', duration=20, deadline=timezone.now() + timezone.timedelta(minutes=40))

        request = self.factory.post(f'/api/quiz/{quiz.slug}/', {'action': 'submit'})
        force_authenticate(request, user=self.user, token=self.token)
        response = QuizView.as_view()(request, quiz.slug)
        self.assertEqual(404, response.status_code)

    def test_submit_quiz_with_remaining_time(self):
        quiz = Quiz.objects.create(title='Quiz', duration=20, deadline=timezone.now() + timezone.timedelta(minutes=40))
        user_quiz = UserQuiz.objects.create(quiz=quiz, user=self.user)
        user_quiz.start_time = timezone.now() - timezone.timedelta(minutes=10)
        user_quiz.save()

        request = self.factory.post(f'/api/quiz/{quiz.slug}/', {'action': 'submit'})
        force_authenticate(request, user=self.user, token=self.token)
        response = QuizView.as_view()(request, quiz.slug)
        self.assertEqual(200, response.status_code)
        self.assertEqual(10 * 60, response.data['remaining_seconds'])
        self.assertTrue(response.data['submitted'])
        self.assertIsNotNone(response.data['submission_time'])

    def test_submit_quiz_with_exceeded_duration(self):
        quiz = Quiz.objects.create(title='Quiz', duration=20, deadline=timezone.now() + timezone.timedelta(minutes=40))
        user_quiz = UserQuiz.objects.create(quiz=quiz, user=self.user)
        user_quiz.start_time = timezone.now() - timezone.timedelta(minutes=30)
        user_quiz.save()

        request = self.factory.post(f'/api/quiz/{quiz.slug}/', {'action': 'submit'})
        force_authenticate(request, user=self.user, token=self.token)
        response = QuizView.as_view()(request, quiz.slug)
        self.assertEqual(200, response.status_code)
        self.assertEqual(-10 * 60, response.data['remaining_seconds'])
        self.assertTrue(response.data['submitted'])
        self.assertIsNotNone(response.data['submission_time'])
