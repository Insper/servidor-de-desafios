from pathlib import Path
from django.http import Http404
from django.test import TestCase
from django.utils import timezone
import shutil, tempfile
import json
import unittest
from code_challenge.models import CodeChallenge, CodeChallengeSubmission, UserChallengeInteraction
from core.models import PyGymUser, Concept, UserConceptInteraction, ChallengeRepo
from quiz.models import Quiz, UserQuiz
from code_challenge.challenge_controller import ChallengeController
from code_challenge.views import get_challenge_or_404
import code_challenge.gitpy as gitpy


class SubmissionSignalTestCase(TestCase):
    def assertInteractions(self, user, challenge, challenge_attempts,
            successful_challenge_attempts, concept_attempts, successful_concept_attempts,
            total_challenges, successful_challenges):
        user_challenge = UserChallengeInteraction.objects.get(user=user, challenge=challenge)
        self.assertEqual(challenge_attempts, user_challenge.attempts)
        self.assertEqual(successful_challenge_attempts, user_challenge.successful_attempts)

        user_concept = UserConceptInteraction.objects.get(user=user, concept=challenge.concept)
        self.assertEqual(concept_attempts, user_concept.attempts)
        self.assertEqual(successful_concept_attempts, user_concept.successful_attempts)
        self.assertEqual(total_challenges, user_concept.total_challenges)
        self.assertEqual(successful_challenges, user_concept.successful_challenges)

    def test_should_send_signal_when_created(self):
        '''When a challenge submission is created for a new challenge, a user-challenge interaction and user-concept interaction are created.'''
        user = PyGymUser.objects.create_user(username='user', password='1234')
        repo = ChallengeRepo.objects.create()
        concept = Concept.objects.create(name='Memoization', slug='algo-memoization')
        challenge = CodeChallenge.objects.create(title="Challenge", slug="challenge", repo=repo, concept=concept)

        CodeChallengeSubmission.objects.create(challenge=challenge, author=user)

        self.assertInteractions(user, challenge, 1, 0, 1, 0, 1, 0)

    def test_should_update_interactions_when_created(self):
        '''When a challenge submission is created for a challenge, the user-challenge interaction and user-concept interaction are updated.'''
        user = PyGymUser.objects.create_user(username='user', password='1234')
        repo = ChallengeRepo.objects.create()
        concept = Concept.objects.create(name='Memoization', slug='algo-memoization')
        other_concept = Concept.objects.create(name='Recursion', slug='recursion')
        main_challenge = CodeChallenge.objects.create(title="Main Challenge", slug="main-challenge", repo=repo, concept=concept)
        other_challenge = CodeChallenge.objects.create(title="Other Challenge", slug="other-challenge", repo=repo, concept=concept)
        challenge_in_other_concept = CodeChallenge.objects.create(title="Challenge in other concept", slug="third-challenge", repo=repo, concept=other_concept)

        # Interactions should be created
        CodeChallengeSubmission.objects.create(challenge=other_challenge, author=user, success=False)
        CodeChallengeSubmission.objects.create(challenge=challenge_in_other_concept, author=user, success=False)
        CodeChallengeSubmission.objects.create(challenge=main_challenge, author=user, success=False)

        self.assertInteractions(user, main_challenge, 1, 0, 2, 0, 2, 0)

        # Now the interactions should be updated
        CodeChallengeSubmission.objects.create(challenge=other_challenge, author=user, success=True)
        CodeChallengeSubmission.objects.create(challenge=challenge_in_other_concept, author=user, success=True)
        CodeChallengeSubmission.objects.create(challenge=main_challenge, author=user, success=True)

        self.assertInteractions(user, main_challenge, 2, 1, 4, 2, 2, 2)

        # Successful count shouldn't change
        CodeChallengeSubmission.objects.create(challenge=other_challenge, author=user, success=False)
        CodeChallengeSubmission.objects.create(challenge=challenge_in_other_concept, author=user, success=False)
        CodeChallengeSubmission.objects.create(challenge=main_challenge, author=user, success=False)

        self.assertInteractions(user, main_challenge, 3, 1, 6, 2, 2, 2)

        # Successful count should change
        CodeChallengeSubmission.objects.create(challenge=other_challenge, author=user, success=True)
        CodeChallengeSubmission.objects.create(challenge=challenge_in_other_concept, author=user, success=True)
        CodeChallengeSubmission.objects.create(challenge=main_challenge, author=user, success=True)

        self.assertInteractions(user, main_challenge, 4, 2, 8, 4, 2, 2)


def save_challenge(base_dir, slug, details, question, tests):
    challenge_dir = base_dir / slug
    try:
        challenge_dir.mkdir(parents=True)
    except FileExistsError:
        pass
    details_file = challenge_dir / 'details.json'
    question_file = challenge_dir / 'question.md'
    test_file = challenge_dir / 'tests.py'
    with open(details_file, 'w', encoding='utf-8') as f:
        json.dump(details, f)
    with open(question_file, 'w', encoding='utf-8') as f:
        f.write(question)
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(tests)
    return details_file, question_file, test_file


def save_trace_challenge(base_dir, slug, details, code, trace):
    challenge_dir = base_dir / 'traces' / slug
    try:
        challenge_dir.mkdir(parents=True)
    except FileExistsError:
        pass
    details_file = challenge_dir / 'details.json'
    code_file = challenge_dir / 'code.py'
    trace_file = challenge_dir / 'trace.json'
    with open(details_file, 'w', encoding='utf-8') as f:
        json.dump(details, f)
    with open(code_file, 'w', encoding='utf-8') as f:
        f.write(code)
    with open(trace_file, 'w', encoding='utf-8') as f:
        f.write(trace)
    return details_file, code_file, trace_file


class ChallengeControllerTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.tmp_path = Path(tempfile.mkdtemp())

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.tmp_path)

    def test_update_smoke_test(self):
        git = gitpy.Git(self.tmp_path)
        controller = ChallengeController(git, 'https://github.com/Insper/design-de-software-exercicios.git')
        controller.update()
        assert True  # Got here, so that's fine

    def test_list_new_challenges(self):
        git = gitpy.Git(self.tmp_path)
        git.init()
        n = 5
        fs = {}
        for c in range(1, n+1):
            for i in range(c, n+1):
                details = {
                    "title": f"Challenge {i} v.{c}",
                    "concept": "function",
                    "terminal": True,
                    "published": True,
                    "function_name": f"solution_{i}",
                }
                question = f'Something about question {i}. Version {c}'
                challenge_name = f'challenge_{i}'
                tests = f'def test_dummy_{c}():\n    pass'
                files = save_challenge(self.tmp_path / 'challenges', challenge_name, details, question, tests)
                fs[challenge_name] = (details, question, tests)
                for f in files:
                    git.add(f)
            git.commit(f'-m "Commit message #{c}."')

        log = git.log()
        assert len(log) == n
        commits = [None]
        for entry in reversed(log):
            commits.append(entry['commit'])

        cm = ChallengeController(git, None)
        for c, commit in enumerate(commits):
            challenges = cm.changed_challenges(last_commit=commit)
            assert len(challenges) == n - c
            for challenge in challenges:
                got_details = challenges[challenge]
                details, question, _ = fs[challenge]
                for k, v in details.items():
                    assert k in got_details
                    assert got_details[k] == v
                assert got_details['question'] == question
                assert got_details['tests_file'] == str(self.tmp_path / 'challenges' / challenge / 'tests.py')

    def test_list_new_trace_challenges(self):
        git = gitpy.Git(self.tmp_path)
        git.init()
        n = 5
        fs = {}
        for c in range(1, n+1):
            for i in range(c, n+1):
                details = {
                    "title": f"Challenge {i} v.{c}",
                    "concept": "variable",
                    "published": True,
                }
                x = 3*i
                y = 4*i
                z = x*y
                challenge_name = f'trace_{i}'
                code = f'''x = {x}
    y = {y}
    z = x * y
    print(f'{{x}} x {{y}} = {{z}}')
    '''
                trace = f'[{{"line_i": 0, "line": "x = {x}", "name_dicts": {{"<module>": {{"x": {x}}}}}, "call_line_i": null, "retval": null, "stdout": []}}, {{"line_i": 1, "line": "y = {y}", "name_dicts": {{"<module>": {{"x": {x}, "y": {y}}}}}, "call_line_i": null, "retval": null, "stdout": []}}, {{"line_i": 2, "line": "z = x * y", "name_dicts": {{"<module>": {{"x": {x}, "y": {y}, "z": {z}}}}}, "call_line_i": null, "retval": null, "stdout": []}}, {{"line_i": 3, "line": "print(\'O ret\u00e2ngulo de lados {{0}} e {{1}} tem \u00e1rea {{2}}\'.format(x, y, z))", "name_dicts": {{"<module>": {{"x": {x}, "y": {y}, "z": {z}}}}}, "call_line_i": null, "retval": null, "stdout": [{{"out": "O ret\u00e2ngulo de lados {x} e {y} tem \u00e1rea {z}", "in": null}}]}}]'
                files = save_trace_challenge(self.tmp_path, challenge_name, details, code, trace)
                fs[challenge_name] = details
                for f in files:
                    git.add(f)
            git.commit(f'-m "Commit message #{c}."')

        log = git.log()
        assert len(log) == n
        commits = [None]
        for entry in reversed(log):
            commits.append(entry['commit'])

        cm = ChallengeController(git, None)
        for c, commit in enumerate(commits):
            challenges = cm.changed_trace_challenges(last_commit=commit)
            assert len(challenges) == n - c
            for challenge in challenges:
                got_details = challenges[challenge]
                details = fs[challenge]
                for k, v in details.items():
                    assert k in got_details
                    assert got_details[k] == v

    def test_list_deleted_challenges(self):
        git = gitpy.Git(self.tmp_path)
        git.init()
        n = 5
        challenge_paths = []
        for i in range(1, n+1):
            details = {
                "title": f"Challenge {i}",
                "concept": "function",
                "terminal": True,
                "published": True,
                "function_name": f"solution_{i}",
            }
            question = f'Something about question {i}.'
            challenge_name = f'challenge_{i}'
            tests = f'def test_dummy():\n    pass'
            files = save_challenge(self.tmp_path / 'challenges', challenge_name, details, question, tests)
            for f in files:
                git.add(f)
            challenge_paths.append(self.tmp_path / 'challenges' / challenge_name)
        git.commit(f'-m "Adding all files."')

        cm = ChallengeController(git, None)
        for i in range(1, n+1):
            challenge = challenge_paths.pop()
            git.rm('-rf', challenge)
            git.commit('-m', f'Removing {challenge}')
            challenges = cm.changed_challenges(last_commit='HEAD^')
            assert len(challenges) == 1
            assert list(challenges.keys())[0] == challenge.name

    def test_list_deleted_trace_challenges(self):
        git = gitpy.Git(self.tmp_path)
        git.init()
        n = 5
        challenge_paths = []
        for i in range(1, n+1):
            details = {
                "title": f"Challenge {i}",
                "concept": "variable",
                "published": True,
            }
            x = 3*i
            y = 4*i
            z = x*y
            challenge_name = f'trace_{i}'
            code = f'''x = {x}
    y = {y}
    z = x * y
    print(f'{{x}} x {{y}} = {{z}}')
    '''
            trace = f'[{{"line_i": 0, "line": "x = {x}", "name_dicts": {{"<module>": {{"x": {x}}}}}, "call_line_i": null, "retval": null, "stdout": []}}, {{"line_i": 1, "line": "y = {y}", "name_dicts": {{"<module>": {{"x": {x}, "y": {y}}}}}, "call_line_i": null, "retval": null, "stdout": []}}, {{"line_i": 2, "line": "z = x * y", "name_dicts": {{"<module>": {{"x": {x}, "y": {y}, "z": {z}}}}}, "call_line_i": null, "retval": null, "stdout": []}}, {{"line_i": 3, "line": "print(\'O ret\u00e2ngulo de lados {{0}} e {{1}} tem \u00e1rea {{2}}\'.format(x, y, z))", "name_dicts": {{"<module>": {{"x": {x}, "y": {y}, "z": {z}}}}}, "call_line_i": null, "retval": null, "stdout": [{{"out": "O ret\u00e2ngulo de lados {x} e {y} tem \u00e1rea {z}", "in": null}}]}}]'
            files = save_trace_challenge(self.tmp_path, challenge_name, details, code, trace)
            for f in files:
                git.add(f)
            challenge_paths.append(self.tmp_path / 'traces' / challenge_name)
        git.commit(f'-m "Adding all files."')

        cm = ChallengeController(git, None)
        for i in range(1, n+1):
            challenge = challenge_paths.pop()
            git.rm('-rf', challenge)
            git.commit('-m', f'Removing {challenge}')
            challenges = cm.changed_trace_challenges(last_commit='HEAD^')
            assert len(challenges) == 1
            assert list(challenges.keys())[0] == challenge.name


class CodeChallengeTestCase(TestCase):
    def setUp(self):
        self.user = PyGymUser.objects.create_user(username='user', password='1234')
        self.repo = ChallengeRepo.objects.create()
        self.concept = Concept.objects.create(name='Memoization', slug='algo-memoization')

    def test_get_saved_challenge(self):
        challenge = CodeChallenge.objects.create(title="Challenge", slug="challenge", repo=self.repo, concept=self.concept)
        loaded = get_challenge_or_404(challenge.slug, self.user)
        self.assertEqual(loaded.slug, challenge.slug)

    def test_get_invalid_challenge(self):
        CodeChallenge.objects.create(title="Challenge", slug="challenge", repo=self.repo, concept=self.concept)
        with self.assertRaises(Http404):
            get_challenge_or_404('invalid-slug', self.user)

    def test_get_unpublished_challenge(self):
        challenge = CodeChallenge.objects.create(title="Challenge", slug="challenge", repo=self.repo, concept=self.concept, published=False)
        with self.assertRaises(Http404):
            get_challenge_or_404(challenge.slug, self.user)

    def test_get_unpublished_challenge_in_quiz(self):
        challenge1 = CodeChallenge.objects.create(title="Challenge 1", slug="challenge1", repo=self.repo, concept=self.concept, published=False)
        challenge2 = CodeChallenge.objects.create(title="Challenge 2", slug="challenge2", repo=self.repo, concept=self.concept, published=False)
        challenges = [challenge1, challenge2]
        quiz = Quiz.objects.create(title='Quiz', duration=20, deadline=timezone.now() + timezone.timedelta(minutes=40))
        quiz.challenges.set(challenges)
        quiz.save()
        uq = UserQuiz.objects.create(quiz=quiz, user=self.user)
        uq.challenges.set(challenges)
        uq.save()

        loaded = get_challenge_or_404(challenge1.slug, self.user)
        self.assertEqual(loaded.slug, challenge1.slug)

    def test_get_unpublished_challenge_in_submitted_quiz(self):
        challenge1 = CodeChallenge.objects.create(title="Challenge 1", slug="challenge1", repo=self.repo, concept=self.concept, published=False)
        challenge2 = CodeChallenge.objects.create(title="Challenge 2", slug="challenge2", repo=self.repo, concept=self.concept, published=False)
        challenges = [challenge1, challenge2]
        quiz = Quiz.objects.create(title='Quiz', duration=20, deadline=timezone.now() + timezone.timedelta(minutes=40))
        quiz.challenges.set(challenges)
        quiz.save()
        uq = UserQuiz.objects.create(quiz=quiz, user=self.user, submitted=True)
        uq.challenges.set(challenges)
        uq.save()

        with self.assertRaises(Http404):
            get_challenge_or_404(challenge1.slug, self.user)

    def test_get_unpublished_challenge_in_not_submitted_quiz_after_timeout(self):
        challenge1 = CodeChallenge.objects.create(title="Challenge 1", slug="challenge1", repo=self.repo, concept=self.concept, published=False)
        challenge2 = CodeChallenge.objects.create(title="Challenge 2", slug="challenge2", repo=self.repo, concept=self.concept, published=False)
        challenges = [challenge1, challenge2]
        quiz = Quiz.objects.create(title='Quiz', duration=20, deadline=timezone.now() + timezone.timedelta(minutes=40))
        quiz.challenges.set(challenges)
        quiz.save()
        uq = UserQuiz.objects.create(quiz=quiz, user=self.user, submitted=False)
        uq.challenges.set(challenges)
        uq.start_time = timezone.now() - timezone.timedelta(minutes=30)
        uq.save()

        with self.assertRaises(Http404):
            get_challenge_or_404(challenge1.slug, self.user)

    def test_get_unpublished_challenge_in_not_submitted_quiz_before_timeout(self):
        challenge1 = CodeChallenge.objects.create(title="Challenge 1", slug="challenge1", repo=self.repo, concept=self.concept, published=False)
        challenge2 = CodeChallenge.objects.create(title="Challenge 2", slug="challenge2", repo=self.repo, concept=self.concept, published=False)
        challenges = [challenge1, challenge2]
        quiz = Quiz.objects.create(title='Quiz', duration=20, deadline=timezone.now() + timezone.timedelta(minutes=40))
        quiz.challenges.set(challenges)
        quiz.save()
        uq = UserQuiz.objects.create(quiz=quiz, user=self.user, submitted=False)
        uq.challenges.set(challenges)
        uq.start_time = timezone.now() - timezone.timedelta(minutes=24)
        uq.save()

        loaded = get_challenge_or_404(challenge1.slug, self.user)
        self.assertEqual(loaded.slug, challenge1.slug)
