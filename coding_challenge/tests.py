from django.test import TestCase
from coding_challenge.models import ChallengeRepo, CodingChallenge, CodingChallengeSubmission, Tag, UserChallengeInteraction, UserTagInteraction
from core.models import PyGymUser


class TagTestCase(TestCase):
    def test_slug_auto_create(self):
        '''Tags without slug are assigned an automatic slug.'''
        tag = Tag.objects.create(name='Tail Recursion')
        self.assertEqual('tail-recursion', tag.slug)

        tag = Tag.objects.create(name='Memoization', slug='algo-memoization')
        self.assertEqual('algo-memoization', tag.slug)

    def test_ordering(self):
        '''Tags are initially ordered by the attribute order, and then by slug.'''
        tag2 = Tag.objects.create(name='tag-a', order=2)
        tag4 = Tag.objects.create(name='tag-c')
        tag3 = Tag.objects.create(name='tag-b')
        tag1 = Tag.objects.create(name='tag-d', order=1)
        expected = [tag1, tag2, tag3, tag4]
        for exp, got in zip(expected, Tag.objects.all()):
            self.assertEqual(exp, got)


class SubmissionSignalTestCase(TestCase):
    def assertInteractions(self, user, challenge, challenge_attempts,
            successful_challenge_attempts, tag_attempts, successful_tag_attempts,
            total_challenges, successful_challenges):
        user_challenge = UserChallengeInteraction.objects.get(user=user, challenge=challenge)
        self.assertEqual(challenge_attempts, user_challenge.attempts)
        self.assertEqual(successful_challenge_attempts, user_challenge.successful_attempts)

        user_tag = UserTagInteraction.objects.get(user=user, tag=challenge.tag)
        self.assertEqual(tag_attempts, user_tag.attempts)
        self.assertEqual(successful_tag_attempts, user_tag.successful_attempts)
        self.assertEqual(total_challenges, user_tag.total_challenges)
        self.assertEqual(successful_challenges, user_tag.successful_challenges)

    def test_should_send_signal_when_created(self):
        '''When a challenge submission is created for a new challenge, a user-challenge interaction and user-tag interaction are created.'''
        user = PyGymUser.objects.create_user(username='user', password='1234')
        repo = ChallengeRepo.objects.create()
        tag = Tag.objects.create(name='Memoization', slug='algo-memoization')
        challenge = CodingChallenge.objects.create(title="Challenge", slug="challenge", repo=repo, tag=tag)

        CodingChallengeSubmission.objects.create(challenge=challenge, author=user)

        self.assertInteractions(user, challenge, 1, 0, 1, 0, 1, 0)

    def test_should_update_interactions_when_created(self):
        '''When a challenge submission is created for a challenge, the user-challenge interaction and user-tag interaction are updated.'''
        user = PyGymUser.objects.create_user(username='user', password='1234')
        repo = ChallengeRepo.objects.create()
        tag = Tag.objects.create(name='Memoization', slug='algo-memoization')
        other_tag = Tag.objects.create(name='Recursion', slug='recursion')
        main_challenge = CodingChallenge.objects.create(title="Main Challenge", slug="main-challenge", repo=repo, tag=tag)
        other_challenge = CodingChallenge.objects.create(title="Other Challenge", slug="other-challenge", repo=repo, tag=tag)
        challenge_in_other_tag = CodingChallenge.objects.create(title="Challenge in other tag", slug="third-challenge", repo=repo, tag=other_tag)

        # Interactions should be created
        CodingChallengeSubmission.objects.create(challenge=other_challenge, author=user, success=False)
        CodingChallengeSubmission.objects.create(challenge=challenge_in_other_tag, author=user, success=False)
        CodingChallengeSubmission.objects.create(challenge=main_challenge, author=user, success=False)

        self.assertInteractions(user, main_challenge, 1, 0, 2, 0, 2, 0)

        # Now the interactions should be updated
        CodingChallengeSubmission.objects.create(challenge=other_challenge, author=user, success=True)
        CodingChallengeSubmission.objects.create(challenge=challenge_in_other_tag, author=user, success=True)
        CodingChallengeSubmission.objects.create(challenge=main_challenge, author=user, success=True)

        self.assertInteractions(user, main_challenge, 2, 1, 4, 2, 2, 2)

        # Successful count shouldn't change
        CodingChallengeSubmission.objects.create(challenge=other_challenge, author=user, success=False)
        CodingChallengeSubmission.objects.create(challenge=challenge_in_other_tag, author=user, success=False)
        CodingChallengeSubmission.objects.create(challenge=main_challenge, author=user, success=False)

        self.assertInteractions(user, main_challenge, 3, 1, 6, 2, 2, 2)

        # Successful count should change
        CodingChallengeSubmission.objects.create(challenge=other_challenge, author=user, success=True)
        CodingChallengeSubmission.objects.create(challenge=challenge_in_other_tag, author=user, success=True)
        CodingChallengeSubmission.objects.create(challenge=main_challenge, author=user, success=True)

        self.assertInteractions(user, main_challenge, 4, 2, 8, 4, 2, 2)
