from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CodeChallengeSubmission, UserChallengeInteraction
from core.models import Concept, UserConceptInteraction


@receiver(post_save, sender=CodeChallengeSubmission, dispatch_uid="48182593106723498")
def post_submission_save(sender, instance, created, raw, using, update_fields, **kwargs):
    if not created:
        return

    author = instance.author
    challenge = instance.challenge

    try:
        user_concept = UserConceptInteraction.objects.get(user=author, concept=challenge.concept)
    except UserConceptInteraction.DoesNotExist:
        user_concept = UserConceptInteraction.objects.create(user=author, concept=challenge.concept)
    try:
        user_challenge = UserChallengeInteraction.objects.get(user=author, challenge=challenge)
    except UserChallengeInteraction.DoesNotExist:
        user_challenge = UserChallengeInteraction.objects.create(user=author, challenge=challenge)
        user_concept.total_challenges += 1

    user_challenge.attempts += 1
    user_concept.attempts += 1
    if instance.success:
        user_challenge.successful_attempts += 1
        user_concept.successful_attempts += 1
        if user_challenge.successful_attempts == 1:
            user_concept.successful_challenges += 1

    user_challenge.save()
    user_concept.save()
