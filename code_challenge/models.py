import os
from django.db import models
import markdown
from django.conf import settings
from core.models import Concept, ChallengeRepo


# Constants
STACKTRACE_FILE_PATTERN = 'File "<string>", '


class CodeChallenge(models.Model):
    title = models.CharField(max_length=1024)
    slug = models.SlugField()
    repo = models.ForeignKey(ChallengeRepo, on_delete=models.CASCADE)
    question = models.TextField()
    published = models.BooleanField(default=True)
    show_stdout = models.BooleanField(default=True)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    function_name = models.CharField(max_length=50, blank=True)
    deleted = models.BooleanField(default=False)

    @property
    def question_html(self):
        return markdown.markdown(self.question, extensions=['extra', 'codehilite'])

    def __str__(self):
        return self.title


def user_challenge_path(instance, filename):
    username = instance.author.username
    slug = instance.challenge.slug
    date_str = instance.creation_date.strftime('%Y_%m_%d_%H_%M_%S_%f')
    filename = f'{slug}/user_{username}/sol{date_str}.py'.format(username, id, date_str)
    return os.path.join('submissions/', filename)


def empty_list():
    return []


class CodeChallengeSubmission(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(CodeChallenge, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    code = models.FileField(upload_to=user_challenge_path)
    success = models.BooleanField(default=False)
    failures = models.JSONField(default=empty_list)
    stack_traces = models.JSONField(default=empty_list)
    stdouts = models.JSONField(default=empty_list)

    def __str__(self):
        return f'{self.author.username}: {self.challenge.title}({self.creation_date}) success[{self.success}]'

    @property
    def safe_stack_traces(self):
        retval = []
        for st in self.stack_traces:
            safe = st
            if 'AssertionError' in safe:
                safe = 'Wrong answer.'
            else:
                start = safe.rfind(STACKTRACE_FILE_PATTERN)
                if start >= 0:
                    safe = safe[start + len(STACKTRACE_FILE_PATTERN):]
            retval.append(safe)
        return retval


class UserChallengeInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(CodeChallenge, on_delete=models.CASCADE)
    attempts = models.IntegerField(default=0)
    successful_attempts = models.IntegerField(default=0)
