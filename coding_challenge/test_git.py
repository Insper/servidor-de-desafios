import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
import gitpy
import pytest


async def create_file(git, filename, content):
    with open(filename, 'w') as f:
        f.write(content)
    await git.add(filename)


@pytest.mark.asyncio
async def test_git():
    _, stdout, sterr = await gitpy.git_cmd('--version')
    assert 'git version' in stdout
    assert not sterr, 'An error occurred when trying to run `git --version`.'


@pytest.mark.asyncio
async def test_clone(tmp_path):
    git = gitpy.Git(tmp_path)
    await git.clone('https://github.com/Insper/design-de-software-exercicios.git')
    assert len(list(tmp_path.iterdir())) > 0


@pytest.mark.asyncio
async def test_clone_in_existing_repo(tmp_path):
    git = gitpy.Git(tmp_path)
    await git.init()
    with pytest.raises(RuntimeError):
        await git.clone('https://github.com/Insper/design-de-software-exercicios.git')
    assert len(list(tmp_path.iterdir())) > 0


@pytest.mark.asyncio
async def test_flow(tmp_path):
    git = gitpy.Git(tmp_path)
    await git.clone('https://github.com/Insper/design-de-software-exercicios.git')
    await git.pull()
    assert len(list(tmp_path.iterdir())) > 0
    await create_file(git, tmp_path / 'new_file.txt', 'Some content in this new file\n')
    await git.commit('-m "Commit message"')


@pytest.mark.asyncio
async def test_empty_dir_not_repo(tmp_path):
    git = gitpy.Git(tmp_path)
    assert not git.is_repo()
    assert not gitpy.Git(Path('dir_that_doesnt_exist')).is_repo()
    await git.init()
    assert git.is_repo()


@pytest.mark.asyncio
async def test_log(tmp_path):
    git = gitpy.Git(tmp_path)
    await git.init()
    filename = tmp_path / 'new_file.txt'
    n = 10
    for i in range(1, n + 1):
        await create_file(git, filename, f'Some content in this new file with changing number: {i}\n')
        await git.commit(f'-m "Commit message #{i}\nMultiple lines."')
    log = await git.log()
    assert len(log) == n
    for i, entry in enumerate(log):
        assert f'#{n-i}' in entry['message']
