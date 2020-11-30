import gitpy
import json
from pathlib import Path


class ChallengeManager:
    def __init__(self, git, repo_url, last_commit=None):
        self.repo_url = repo_url
        self.last_commit = last_commit
        self.git = git

    async def update(self):
        if self.git.is_repo():
            await self.git.pull()
        else:
            await self.git.clone(self.repo_url)

    async def changed_challenges(self, challenges_dir='challenges', details_file='details.json', question_file='question.md'):
        if self.last_commit:
            cdir = str(Path(self.git.base_dir / challenges_dir).absolute())
            challenge_dirs = await self.git.changed_files(self.last_commit)
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
        challenge_dirs = [d for d in challenge_dirs if d.is_dir()]

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
            except FileNotFoundError:
                pass

        return all_challenges
