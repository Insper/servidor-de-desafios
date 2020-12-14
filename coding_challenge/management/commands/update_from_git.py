import asyncio
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from coding_challenge import gitpy
from coding_challenge.challenge_manager import ChallengeManager
from coding_challenge.models import CodingChallenge, ChallengeRepo, Tag


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
        tag = Tag.objects.get(slug=data['tag'])
        try:
            challenge = CodingChallenge.objects.get(slug=slug, repo=repo)
            challenge.title = data['title']
            challenge.question = data['question']
            challenge.published = data['published']
            challenge.show_stdout = data['terminal']
            challenge.function_name = data['function_name']
            challenge.save()
        except CodingChallenge.DoesNotExist:
            challenge = CodingChallenge.objects.create(
                title=data['title'],
                slug=slug,
                repo=repo,
                question=data['question'],
                published=data['published'],
                show_stdout=data['terminal'],
                function_name=data['function_name'],
                tag=tag,
            )
            challenge.save()
        return challenge

    def delete(self, slug, repo):
        try:
            challenge = CodingChallenge.objects.get(slug=slug, repo=repo)
            challenge.deleted = True
            challenge.save()
        except CodingChallenge.DoesNotExist:
            return

    def create_tags(self, tags_file):
        with open(tags_file) as f:
            for tag in [t.strip() for t in f.read().split() if t.strip()]:
                args = tag.split(',')
                if len(args) > 2:
                    Tag.objects.get_or_create(name=args[0], slug=args[1], order=int(args[2]))
                elif len(args) > 1:
                    Tag.objects.get_or_create(name=args[0], slug=args[1])
                else:
                    Tag.objects.get_or_create(name=args[0])

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

        self.create_tags(repo_dir / 'tags.txt')

        for slug, data in updated_challenges.items():
            if data:
                self.update_or_create(slug, data, repo)
            else:
                self.delete(slug, repo)

        repo.last_commit = log[0]['commit']
        repo.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully updated repo "{repo}"'))
