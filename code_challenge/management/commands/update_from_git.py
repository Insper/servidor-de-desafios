import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from code_challenge import gitpy
from code_challenge.challenge_controller import ChallengeController
from code_challenge.models import CodeChallenge
from trace_challenge.models import TraceChallenge
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

    def update_or_create_code_challenge(self, slug, data, repo):
        concept = Concept.objects.get(slug=data['concept'])
        try:
            challenge = CodeChallenge.objects.get(slug=slug, repo=repo)
            challenge.title = data['title']
            challenge.question = data['question']
            challenge.concept = concept
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
        return challenge

    def delete_code_challenge(self, slug, repo):
        try:
            challenge = CodeChallenge.objects.get(slug=slug, repo=repo)
            challenge.deleted = True
            challenge.save()
        except CodeChallenge.DoesNotExist:
            return

    def update_or_create_trace_challenge(self, slug, data, repo):
        concept = Concept.objects.get(slug=data['concept'])
        try:
            challenge = TraceChallenge.objects.get(slug=slug, repo=repo)
            challenge.title = data['title']
            challenge.concept = concept
            challenge.published = data['published']
            challenge.save()
        except TraceChallenge.DoesNotExist:
            challenge = TraceChallenge.objects.create(
                title=data['title'],
                concept=concept,
                slug=slug,
                repo=repo,
                published=data['published'],
            )
        return challenge

    def delete_trace_challenge(self, slug, repo):
        try:
            challenge = TraceChallenge.objects.get(slug=slug, repo=repo)
            challenge.deleted = True
            challenge.save()
        except TraceChallenge.DoesNotExist:
            return

    def copy_page_data(self, page_dir):
        slug = page_dir.name
        src = page_dir / 'raw' / slug
        if src.is_dir():
            dst = settings.CONTENT_RAW_DIR / slug
            if dst.exists():
                shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst)

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
        controller = ChallengeController(git, repo.remote)

        controller.update()
        updated_challenges = controller.changed_challenges(last_commit=repo.last_commit)
        updated_traces = controller.changed_trace_challenges(last_commit=repo.last_commit)
        updated_pages = controller.changed_pages(last_commit=repo.last_commit)
        log = git.log(last=1)

        self.create_concepts(repo_dir / 'concepts.txt')

        for slug, data in updated_challenges.items():
            if data:
                self.update_or_create_code_challenge(slug, data, repo)
            else:
                self.delete_code_challenge(slug, repo)

        for slug, data in updated_traces.items():
            if data:
                self.update_or_create_trace_challenge(slug, data, repo)
            else:
                self.delte_trace_challenge(slug, repo)

        for page_dir in updated_pages:
            self.copy_page_data(page_dir)

        repo.last_commit = log[0]['commit']
        repo.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully updated repo "{repo}"'))
