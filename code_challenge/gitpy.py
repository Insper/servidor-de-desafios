from pathlib import Path
import subprocess


def git_cmd(cmd, cwd=None):
    if isinstance(cmd, str):
        cmd = [cmd]
    full_cmd = ['git'] + cmd
    proc = subprocess.run(full_cmd, capture_output=True, cwd=cwd)

    return proc.returncode, proc.stdout.decode(), proc.stderr.decode()


class Git:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def _git(self, cmd, args=None):
        if args is None:
            args = []
        retcode, stdout, stderr = git_cmd([cmd] + list(args), self.base_dir)

        return retcode, stdout, stderr

    def init(self):
        self._git('init')

    def clone(self, url):
        if self.is_repo():
            raise RuntimeError('There is already a git repo in {self.base_dir}')
        git_cmd(['clone', url, self.base_dir])

    def is_repo(self):
        path = Path(self.base_dir)
        return path.exists() and (path / '.git').is_dir()

    def status(self):
        return self._git('status')

    def pull(self, *pull_args):
        self._git('pull', args=pull_args)

    def add(self, *add_args):
        self._git('add', args=add_args)

    def commit(self, *commit_args):
        self._git('commit', args=commit_args)

    def push(self, *push_args):
        self._git('push', args=push_args)

    def rm(self, *rm_args):
        self._git('rm', args=rm_args)

    def log(self, *log_args, last=None):
        if last:
            log_args += ('-n', f'{last}')
        _, entries_str, _ = self._git('log', args=log_args)

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

    def changed_files(self, sha):
        _, files, _ = self._git('diff', ['--name-only', sha])
        return [self.base_dir / f.strip() for f in files.split('\n') if f.strip()]
