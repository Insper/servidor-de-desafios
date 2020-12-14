from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CodingChallengeSubmission, UserChallengeInteraction, UserTagInteraction


@receiver(post_save, sender=CodingChallengeSubmission, dispatch_uid="48182593106723498")
def post_submission_save(sender, instance, created, raw, using, update_fields, **kwargs):
    if not created:
        return

    author = instance.author
    challenge = instance.challenge

    try:
        user_tag = UserTagInteraction.objects.get(user=author, tag=challenge.tag)
    except UserTagInteraction.DoesNotExist:
        user_tag = UserTagInteraction.objects.create(user=author, tag=challenge.tag)
    try:
        user_challenge = UserChallengeInteraction.objects.get(user=author, challenge=challenge)
    except UserChallengeInteraction.DoesNotExist:
        user_challenge = UserChallengeInteraction.objects.create(user=author, challenge=challenge)
        user_tag.total_challenges += 1

    user_challenge.attempts += 1
    user_tag.attempts += 1
    if instance.success:
        user_challenge.successful_attempts += 1
        user_tag.successful_attempts += 1
        if user_challenge.successful_attempts == 1:
            user_tag.successful_challenges += 1

    user_challenge.save()
    user_tag.save()
