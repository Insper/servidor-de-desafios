import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from challenge_manager import ChallengeManager
import json
import pytest
import gitpy


def save_challenge(base_dir, slug, details, question, tests):
    challenge_dir = base_dir / 'challenges' / slug
    try:
        challenge_dir.mkdir(parents=True)
    except FileExistsError:
        pass
    details_file = challenge_dir / 'details.json'
    question_file = challenge_dir / 'question.md'
    test_file = challenge_dir / 'tests.py'
    with open(details_file, 'w') as f:
        json.dump(details, f)
    with open(question_file, 'w') as f:
        f.write(question)
    with open(test_file, 'w') as f:
        f.write(tests)
    return details_file, question_file, test_file


@pytest.mark.asyncio
async def test_update_smoke_test(tmp_path):
    git = gitpy.Git(tmp_path)
    cm = ChallengeManager(git, 'https://github.com/Insper/design-de-software-exercicios.git')
    await cm.update()
    assert True  # Got here, so that's fine


@pytest.mark.asyncio
async def test_list_new_challenges(tmp_path):
    git = gitpy.Git(tmp_path)
    await git.init()
    n = 5
    fs = {}
    for c in range(1, n+1):
        for i in range(c, n+1):
            details = {
                "title": f"Challenge {i} v.{c}",
                "concept": "function",
                "terminal": True,
                "published": True,
                "function_name": f"solution_{i}",
            }
            question = f'Something about question {i}. Version {c}'
            challenge_name = f'challenge_{i}'
            tests = f'def test_dummy_{c}():\n    pass'
            files = save_challenge(tmp_path, challenge_name, details, question, tests)
            fs[challenge_name] = (details, question, tests)
            for f in files:
                await git.add(f)
        await git.commit(f'-m "Commit message #{c}."')

    log = await git.log()
    assert len(log) == n
    commits = [None]
    for entry in reversed(log):
        commits.append(entry['commit'])

    cm = ChallengeManager(git, None)
    for c, commit in enumerate(commits):
        challenges = await cm.changed_challenges(last_commit=commit)
        assert len(challenges) == n - c
        for challenge in challenges:
            got_details = challenges[challenge]
            details, question, _ = fs[challenge]
            for k, v in details.items():
                assert k in got_details
                assert got_details[k] == v
            assert got_details['question'] == question
            assert got_details['tests_file'] == str(tmp_path / 'challenges' / challenge / 'tests.py')


@pytest.mark.asyncio
async def test_list_deleted_challenges(tmp_path):
    git = gitpy.Git(tmp_path)
    await git.init()
    n = 5
    challenge_paths = []
    for i in range(1, n+1):
        details = {
            "title": f"Challenge {i}",
            "concept": "function",
            "terminal": True,
            "published": True,
            "function_name": f"solution_{i}",
        }
        question = f'Something about question {i}.'
        challenge_name = f'challenge_{i}'
        tests = f'def test_dummy():\n    pass'
        files = save_challenge(tmp_path, challenge_name, details, question, tests)
        for f in files:
            await git.add(f)
        challenge_paths.append(tmp_path / 'challenges' / challenge_name)
    await git.commit(f'-m "Adding all files."')

    cm = ChallengeManager(git, None)
    for i in range(1, n+1):
        challenge = challenge_paths.pop()
        await git.rm('-rf', challenge)
        await git.commit('-m', f'Removing {challenge}')
        challenges = await cm.changed_challenges(last_commit='HEAD^')
        assert len(challenges) == 1
        assert list(challenges.keys())[0] == challenge.name
