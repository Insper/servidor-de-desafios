from django.core.management.base import BaseCommand
from code_challenge.repo import update_from_git
from core.models import ChallengeRepo


class Command(BaseCommand):
    help = 'Updates challenges from git repo'

    def get_choice(self, msg, choices):
        if not choices:
            raise RuntimeError('There are no repos available')
        if len(choices) == 1:
            return choices[0]
        ret = None
        while ret is None:
            print(msg)
            for i, c in enumerate(choices, 1):
                print(f'{i}) {c}')
            try:
                ret = choices[int(input('Choice: ')) - 1]
            except (IndexError, ValueError, AssertionError):
                print('Invalid index.')
        return ret

    def handle(self, *args, **options):
        repos = ChallengeRepo.objects.all()
        try:
            repo = self.get_choice('Select repo:', repos)
        except:
            self.stdout.write(self.style.WARNING(f'No repo configured'))
            return

        update_from_git(repo)

        self.stdout.write(self.style.SUCCESS(f'Successfully updated repo "{repo}"'))
