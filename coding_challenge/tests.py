from django.test import TestCase
from coding_challenge.models import ChallengeRepo, CodingChallenge, CodingChallengeSubmission, UserChallengeInteraction
from core.models import PyGymUser, Concept, UserConceptInteraction


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
        challenge = CodingChallenge.objects.create(title="Challenge", slug="challenge", repo=repo, concept=concept)

        CodingChallengeSubmission.objects.create(challenge=challenge, author=user)

        self.assertInteractions(user, challenge, 1, 0, 1, 0, 1, 0)

    def test_should_update_interactions_when_created(self):
        '''When a challenge submission is created for a challenge, the user-challenge interaction and user-concept interaction are updated.'''
        user = PyGymUser.objects.create_user(username='user', password='1234')
        repo = ChallengeRepo.objects.create()
        concept = Concept.objects.create(name='Memoization', slug='algo-memoization')
        other_concept = Concept.objects.create(name='Recursion', slug='recursion')
        main_challenge = CodingChallenge.objects.create(title="Main Challenge", slug="main-challenge", repo=repo, concept=concept)
        other_challenge = CodingChallenge.objects.create(title="Other Challenge", slug="other-challenge", repo=repo, concept=concept)
        challenge_in_other_concept = CodingChallenge.objects.create(title="Challenge in other concept", slug="third-challenge", repo=repo, concept=other_concept)

        # Interactions should be created
        CodingChallengeSubmission.objects.create(challenge=other_challenge, author=user, success=False)
        CodingChallengeSubmission.objects.create(challenge=challenge_in_other_concept, author=user, success=False)
        CodingChallengeSubmission.objects.create(challenge=main_challenge, author=user, success=False)

        self.assertInteractions(user, main_challenge, 1, 0, 2, 0, 2, 0)

        # Now the interactions should be updated
        CodingChallengeSubmission.objects.create(challenge=other_challenge, author=user, success=True)
        CodingChallengeSubmission.objects.create(challenge=challenge_in_other_concept, author=user, success=True)
        CodingChallengeSubmission.objects.create(challenge=main_challenge, author=user, success=True)

        self.assertInteractions(user, main_challenge, 2, 1, 4, 2, 2, 2)

        # Successful count shouldn't change
        CodingChallengeSubmission.objects.create(challenge=other_challenge, author=user, success=False)
        CodingChallengeSubmission.objects.create(challenge=challenge_in_other_concept, author=user, success=False)
        CodingChallengeSubmission.objects.create(challenge=main_challenge, author=user, success=False)

        self.assertInteractions(user, main_challenge, 3, 1, 6, 2, 2, 2)

        # Successful count should change
        CodingChallengeSubmission.objects.create(challenge=other_challenge, author=user, success=True)
        CodingChallengeSubmission.objects.create(challenge=challenge_in_other_concept, author=user, success=True)
        CodingChallengeSubmission.objects.create(challenge=main_challenge, author=user, success=True)

        self.assertInteractions(user, main_challenge, 4, 2, 8, 4, 2, 2)
