import json
from pathlib import Path
import shutil
from django.conf import settings


class ChallengeManager:
    def __init__(self, git, repo_url):
        self.repo_url = repo_url
        self.git = git

    async def update(self):
        if self.git.is_repo():
            await self.git.pull()
        else:
            await self.git.clone(self.repo_url)

    async def changed_challenges(self, challenges_dir='challenges', details_file='details.json', question_file='question.md', raw_dir='raw', last_commit=None):
        if last_commit:
            cdir = str(Path(self.git.base_dir / challenges_dir).absolute())
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
            challenge_dirs = (self.git.base_dir / challenges_dir).iterdir()
        challenge_dirs = [d for d in challenge_dirs if d.is_dir() or not d.exists()]

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


def test_code_for(challenge):
    challenges_dir = settings.CHALLENGES_DIR / challenge.repo.slug / 'challenges'
    tests_file = challenges_dir / challenge.slug / 'tests.py'
    try:
        with open(tests_file) as f:
            return f.read()
    except FileNotFoundError:
        return None
