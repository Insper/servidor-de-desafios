import gitpy
import json


async def update_challenges(base_dir, repo_url, challenges_dir='challenges', details_file='details.json', question_file='question.md'):
    git = gitpy.Git(base_dir)
    if git.is_repo():
        await git.pull()
    else:
        await git.clone(repo_url)

    all_challenges = []
    for challenge_dir in (base_dir / challenges_dir).iterdir():
        if not challenge_dir.is_dir():
            continue

        with open(challenge_dir / details_file) as f:
            details = json.load(f)
        with open(challenge_dir / question_file) as f:
            question = f.read()
        tests_file = challenge_dir / 'tests.py'
        details['question'] = question
        details['tests_file'] = str(tests_file)
        all_challenges.append(details)

    # TODO ONLY UPDATE WHAT CHANGED SINCE LAST COMMIT (WILL PROBABLY NEED TO STORE COMMIT HASH)
