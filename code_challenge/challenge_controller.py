import json
from pathlib import Path
import shutil
from django.conf import settings


class ChallengeController:
    def __init__(self, git, repo_url):
        self.repo_url = repo_url
        self.git = git

    async def update(self):
        if self.git.is_repo():
            await self.git.pull()
        else:
            await self.git.clone(self.repo_url)

    async def list_changed_dirs(self, root_dir, last_commit=None):
        if last_commit:
            cdir = str(Path(self.git.base_dir / root_dir).absolute())
            challenge_dirs = await self.git.changed_files(last_commit)
            tmp = challenge_dirs
            challenge_dirs = set()
            for d in tmp:
                if cdir not in str(d.absolute()):
                    continue
                while cdir != str(d.parent.absolute()):
                    d = d.parent
                challenge_dirs.add(d)
            challenge_dirs = list(challenge_dirs)
        else:
            challenge_dirs = (self.git.base_dir / root_dir).iterdir()
        return [d for d in challenge_dirs if d.is_dir() or not d.exists()]

    async def changed_challenges(self, challenges_dir='challenges', details_file='details.json', question_file='question.md', raw_dir='raw', last_commit=None):
        challenge_dirs = await self.list_changed_dirs(challenges_dir, last_commit)

        all_challenges = {}
        for challenge_dir in challenge_dirs:
            try:
                with open(challenge_dir / details_file) as f:
                    details = json.load(f)
                with open(challenge_dir / question_file) as f:
                    question = f.read()
                tests_file = challenge_dir / 'tests.py'
                details['question'] = question
                details['tests_file'] = str(tests_file)
                all_challenges[challenge_dir.name] = details
                slug = challenge_dir.name
                src = challenge_dir / raw_dir / slug
                if src.is_dir():
                    dst = settings.CHALLENGES_RAW_DIR / slug
                    if (dst).exists():
                        shutil.rmtree(dst, ignore_errors=True)
                    shutil.copytree(src, dst)
            except FileNotFoundError:
                if not challenge_dir.is_dir():
                    all_challenges[challenge_dir.name] = None

        return all_challenges

    async def changed_trace_challenges(self, root_dir='traces', details_file='details.json', last_commit=None):
        trace_dirs = await self.list_changed_dirs(root_dir, last_commit)

        all_traces = {}
        for trace_dir in trace_dirs:
            try:
                with open(trace_dir / details_file) as f:
                    details = json.load(f)
                all_traces[trace_dir.name] = details
            except FileNotFoundError:
                if not trace_dir.is_dir():
                    all_traces[trace_dir.name] = None

        return all_traces

    async def changed_pages(self, root_dir='pages', last_commit=None):
        return await self.list_changed_dirs(root_dir, last_commit)


def test_code_for(challenge):
    challenges_dir = settings.CHALLENGES_DIR / challenge.repo.slug / 'challenges'
    tests_file = challenges_dir / challenge.slug / 'tests.py'
    try:
        with open(tests_file) as f:
            return f.read()
    except FileNotFoundError:
        return None
