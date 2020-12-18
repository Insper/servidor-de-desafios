import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings
from code_challenge import gitpy
from code_challenge.challenge_manager import ChallengeManager
from code_challenge.models import CodeChallenge
from core.models import Concept, ChallengeRepo


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

    def update_or_create(self, slug, data, repo):
        concept = Concept.objects.get(slug=data['concept'])
        try:
            challenge = CodeChallenge.objects.get(slug=slug, repo=repo)
            challenge.title = data['title']
            challenge.question = data['question']
            challenge.published = data['published']
            challenge.show_stdout = data['terminal']
            challenge.function_name = data['function_name']
            challenge.save()
        except CodeChallenge.DoesNotExist:
            challenge = CodeChallenge.objects.create(
                title=data['title'],
                slug=slug,
                repo=repo,
                question=data['question'],
                published=data['published'],
                show_stdout=data['terminal'],
                function_name=data['function_name'],
                concept=concept,
            )
            challenge.save()
        return challenge

    def delete(self, slug, repo):
        try:
            challenge = CodeChallenge.objects.get(slug=slug, repo=repo)
            challenge.deleted = True
            challenge.save()
        except CodeChallenge.DoesNotExist:
            return

    def create_concepts(self, concepts_file):
        with open(concepts_file) as f:
            for concept in [t.strip() for t in f.read().split() if t.strip()]:
                args = concept.split(',')
                if len(args) > 2:
                    Concept.objects.get_or_create(name=args[0], slug=args[1], order=int(args[2]))
                elif len(args) > 1:
                    Concept.objects.get_or_create(name=args[0], slug=args[1])
                else:
                    Concept.objects.get_or_create(name=args[0])

    def handle(self, *args, **options):
        repos = ChallengeRepo.objects.all()
        repo = self.get_choice('Select repo:', repos)

        repo_dir = settings.CHALLENGES_DIR / repo.slug
        git = gitpy.Git(repo_dir)
        cm = ChallengeManager(git, repo.remote)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(cm.update())
        updated_challenges = loop.run_until_complete(cm.changed_challenges(last_commit=repo.last_commit))
        log = loop.run_until_complete(git.log(last=1))

        self.create_concepts(repo_dir / 'concepts.txt')

        for slug, data in updated_challenges.items():
            if data:
                self.update_or_create(slug, data, repo)
            else:
                self.delete(slug, repo)

        repo.last_commit = log[0]['commit']
        repo.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully updated repo "{repo}"'))
