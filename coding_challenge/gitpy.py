import asyncio
from pathlib import Path


async def git_cmd(cmd, cwd=None):
    proc = await asyncio.create_subprocess_shell(
        f'git {cmd}',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd)

    stdout, stderr = await proc.communicate()

    return proc.returncode, stdout.decode(), stderr.decode()


class Git:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    async def _git(self, cmd, args=None):
        if args is None:
            args = []
        return await git_cmd(f'{cmd} {" ".join(str(arg) for arg in args)}', self.base_dir)

    async def init(self):
        await self._git(f'init')

    async def clone(self, url):
        if self.is_repo():
            raise RuntimeError('There is already a git repo in {self.base_dir}')
        await git_cmd(f'clone {url} {self.base_dir}')

    def is_repo(self):
        path = Path(self.base_dir)
        return path.exists() and (path / '.git').is_dir()

    async def pull(self, *pull_args):
        await self._git(f'pull', args=pull_args)

    async def add(self, *add_args):
        await self._git(f'add', args=add_args)

    async def commit(self, *commit_args):
        await self._git(f'commit', args=commit_args)

    async def push(self, *push_args):
        await self._git(f'push', args=push_args)

    async def log(self, *log_args):
        _, entries_str, _ = await self._git(f'log', args=log_args)

        commit_pattern = 'commit '
        author_pattern = 'Author: '
        date_pattern = 'Date:   '
        commit = None
        author = None
        date = None
        msg = None
        commits = []
        for line in entries_str.split('\n'):
            if line.startswith(commit_pattern):
                if commit:
                    commits.append({
                        'commit': commit,
                        'author': author,
                        'date': date,
                        'message': msg.strip(),
                    })
                commit = line[line.index(commit_pattern) + len(commit_pattern):]
                msg = None
            elif line.startswith(author_pattern):
                author = line[line.index(author_pattern) + len(author_pattern):]
            elif line.startswith(date_pattern):
                date = line[line.index(date_pattern) + len(date_pattern):]
            else:
                if msg is None:
                    msg = ''
                msg += line.strip() + '\n'
        if commit:
            commits.append({
                'commit': commit,
                'author': author,
                'date': date,
                'message': msg.strip(),
            })
        return commits
