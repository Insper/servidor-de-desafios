from django.core.management.base import BaseCommand
from django.conf import settings
from code_challenge.models import CodeChallengeSubmission, UserChallengeInteraction


class Command(BaseCommand):
    help = 'Updates challenges from git repo'

    def handle(self, *args, **options):
        interactions = UserChallengeInteraction.objects.filter(latest_submission__isnull=True, attempts__gt=0)

        success = 0
        errors = 0
        to_update = []
        for interaction in interactions:
            try:
                submission = CodeChallengeSubmission.objects.filter(author=interaction.user, challenge=interaction.challenge).latest('pk')
                interaction.latest_submission = submission
                to_update.append(interaction)
                success += 1
            except CodeChallengeSubmission.DoesNotExist:
                errors += 1
        if to_update:
            UserChallengeInteraction.objects.bulk_update(to_update, ['latest_submission'])

        if errors:
            self.stdout.write(self.style.WARNING(f'{errors} submissions not updated'))
        self.stdout.write(self.style.SUCCESS(f'{success} submissions updated'))
