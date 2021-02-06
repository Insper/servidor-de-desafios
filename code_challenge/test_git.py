import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
import gitpy
import pytest


def add_file(git, filename, content):
    with open(filename, 'w') as f:
        f.write(content)
    git.add(filename)


def test_git():
    _, stdout, sterr = gitpy.git_cmd('--version')
    assert 'git version' in stdout
    assert not sterr, 'An error occurred when trying to run `git --version`.'


def test_clone(tmp_path):
    git = gitpy.Git(tmp_path)
    git.clone('https://github.com/Insper/design-de-software-exercicios.git')
    assert len(list(tmp_path.iterdir())) > 0


def test_clone_in_existing_repo(tmp_path):
    git = gitpy.Git(tmp_path)
    git.init()
    with pytest.raises(RuntimeError):
        git.clone('https://github.com/Insper/design-de-software-exercicios.git')
    assert len(list(tmp_path.iterdir())) > 0


def test_flow(tmp_path):
    git = gitpy.Git(tmp_path)
    git.clone('https://github.com/Insper/design-de-software-exercicios.git')
    git.pull()
    assert len(list(tmp_path.iterdir())) > 0
    add_file(git, tmp_path / 'new_file.txt', 'Some content in this new file\n')
    git.commit('-m "Commit message"')


def test_empty_dir_not_repo(tmp_path):
    git = gitpy.Git(tmp_path)
    assert not git.is_repo()
    assert not gitpy.Git(Path('dir_that_doesnt_exist')).is_repo()
    git.init()
    assert git.is_repo()


def test_log(tmp_path):
    git = gitpy.Git(tmp_path)
    git.init()
    filename = tmp_path / 'new_file.txt'
    n = 10
    for i in range(1, n + 1):
        add_file(git, filename, f'Some content in this new file with changing number: {i}\n')
        git.commit(f'-m "Commit message #{i}\nMultiple lines."')
    # Get all
    log = git.log()
    assert len(log) == n
    for i, entry in enumerate(log):
        assert f'#{n-i}' in entry['message']
    # Get last half
    half = n // 2
    log = git.log(last=half)
    assert len(log) == half
    for i, entry in enumerate(log):
        assert f'#{n-i}' in entry['message']


def test_list_file_changes(tmp_path):
    git = gitpy.Git(tmp_path)
    git.init()
    n = 5
    filenames = [tmp_path / f'new_file_{i}.txt' for i in range(1, n+1)]
    for i in range(1, n+2):
        for j in range(max(i-2, 0), n):
            add_file(git, filenames[j], f'Some content in this new file with changing number: {j}.\nWith something else that is fixed: {i}.')
        git.commit(f'-m "Commit message #{i}\nMultiple lines."')
    log = git.log()
    assert len(log) == n + 1
    for i, entry in enumerate(reversed(log)):
        changed = git.changed_files(entry['commit'])
        assert len(changed) == n - i
        assert set(changed) == set(filenames[i:])


def test_list_file_changes_with_deleted_files(tmp_path):
    filename = tmp_path / 'text.txt'

    git = gitpy.Git(tmp_path)
    git.init()
    add_file(git, filename, 'Some text')
    git.commit(f'-m "Adding file"')
    git.rm(filename)
    git.commit(f'-m "Removing file"')
    changed_files = git.changed_files('HEAD^')
    assert changed_files[0] == filename
