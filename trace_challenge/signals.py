from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TraceStateSubmission, UserTraceChallengeInteraction
from core.models import UserConceptInteraction


@receiver(post_save, sender=TraceStateSubmission, dispatch_uid="49731856745193756")
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
        user_challenge = UserTraceChallengeInteraction.objects.get(user=author, challenge=challenge)
    except UserTraceChallengeInteraction.DoesNotExist:
        user_challenge = UserTraceChallengeInteraction.objects.create(user=author, challenge=challenge)
        user_concept.total_challenges += 1

    user_challenge.attempts += 1
    if instance.success:
        user_challenge.successful_attempts += 1
        user_challenge.latest_state = max(user_challenge.latest_state, instance.state_index)
        if instance.is_last and not user_challenge.completed:
            user_challenge.completed = True
            user_concept.successful_challenges += 1

    user_challenge.save()
    user_concept.save()
