import shutil
from django.conf import settings
import requests
from code_challenge import gitpy
from code_challenge.challenge_controller import ChallengeController
from code_challenge.models import CodeChallenge
from core.models import Concept, FrontendUpdateUrl
from trace_challenge.models import TraceChallenge


def update_from_git(repo):
    repo_dir = settings.CHALLENGES_DIR / repo.slug
    git = gitpy.Git(repo_dir)
    controller = ChallengeController(git, repo.remote)

    controller.update()
    updated_challenges = controller.changed_challenges(last_commit=repo.last_commit)
    updated_traces = controller.changed_trace_challenges(last_commit=repo.last_commit)
    updated_pages = controller.changed_pages(last_commit=repo.last_commit)
    log = git.log(last=1)

    create_concepts(repo_dir / 'concepts.txt')

    for slug, data in updated_challenges.items():
        if data:
            update_or_create_code_challenge(slug, data, repo)
        else:
            delete_code_challenge(slug, repo)

    for slug, data in updated_traces.items():
        if data:
            update_or_create_trace_challenge(slug, data, repo)
        else:
            delete_trace_challenge(slug, repo)

    for page_dir in updated_pages:
        copy_page_data(page_dir)

    repo.last_commit = log[0]['commit']
    repo.save()

    trigger_frontend_build()


def create_concepts(concepts_file):
    with open(concepts_file, encoding='utf-8') as f:
        for concept in [t.strip() for t in f.read().split() if t.strip()]:
            args = concept.split(',')
            if len(args) > 2:
                c, _ = Concept.objects.get_or_create(name=args[0], slug=args[1])
                c.order = int(args[2])
                c.save()
            elif len(args) > 1:
                Concept.objects.get_or_create(name=args[0], slug=args[1])
            else:
                Concept.objects.get_or_create(name=args[0])


def update_or_create_code_challenge(slug, data, repo):
    concept = Concept.objects.get(slug=data['concept'])
    try:
        challenge = CodeChallenge.objects.get(slug=slug, repo=repo)
        challenge.title = data['title']
        challenge.repo = repo
        challenge.question = data['question']
        challenge.concept = concept
        challenge.published = data['published']
        challenge.show_stdout = data['terminal']
        challenge.function_name = data['function_name']
        challenge.weight = data['weight']
        challenge.difficulty = data['difficulty']
        challenge.deleted = False
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
            weight=data['weight'],
            difficulty=data['difficulty'],
            concept=concept,
        )
    return challenge


def delete_code_challenge(slug, repo):
        try:
            challenge = CodeChallenge.objects.get(slug=slug, repo=repo)
            challenge.deleted = True
            challenge.save()
        except CodeChallenge.DoesNotExist:
            return


def update_or_create_trace_challenge(slug, data, repo):
    concept = Concept.objects.get(slug=data['concept'])
    try:
        challenge = TraceChallenge.objects.get(slug=slug, repo=repo)
        challenge.title = data['title']
        challenge.concept = concept
        challenge.published = data['published']
        challenge.repo = repo
        challenge.deleted = False
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


def delete_trace_challenge(slug, repo):
    try:
        challenge = TraceChallenge.objects.get(slug=slug, repo=repo)
        challenge.deleted = True
        challenge.save()
    except TraceChallenge.DoesNotExist:
        return


def copy_page_data(page_dir):
    slug = page_dir.name
    src = page_dir / 'raw' / slug
    if src.is_dir():
        dst = settings.CONTENT_RAW_DIR / slug
        if dst.exists():
            shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(src, dst)


def trigger_frontend_build():
    urls = FrontendUpdateUrl.objects.all()
    # More info: https://vercel.com/docs/concepts/git/deploy-hooks
    for frontend in urls:
        requests.get(str(frontend.url))
