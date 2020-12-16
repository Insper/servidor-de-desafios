import os
from collections import namedtuple
from django.db import models
from django.utils.text import slugify
import markdown
from django.conf import settings


# Constants
FEEDBACK_SEP = '|||'
STACKTRACE_SEP = '<|>|<|>'
STACKTRACE_FILE_PATTERN = 'File "<string>", '


class Tag(models.Model):
    name = models.CharField(max_length=128)
    slug = models.CharField(max_length=128)
    order = models.IntegerField(default=99)

    class Meta:
        ordering = ['order', 'slug']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ChallengeRepo(models.Model):
    remote = models.URLField()
    slug = models.SlugField()
    last_commit = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.slug} ({self.remote})'


class CodingChallenge(models.Model):
    title = models.CharField(max_length=1024)
    slug = models.SlugField()
    repo = models.ForeignKey(ChallengeRepo, on_delete=models.CASCADE)
    question = models.TextField()
    published = models.BooleanField(default=True)
    show_stdout = models.BooleanField(default=True)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
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


class CodingChallengeSubmission(models.Model):
    ErrorData = namedtuple('ErrorData', 'message,stacktrace,stdout')

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(CodingChallenge, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    code = models.FileField(upload_to=user_challenge_path)
    success = models.BooleanField(default=False)
    feedback = models.TextField(blank=True)
    errors = models.TextField(blank=True)
    stdouts = models.TextField(blank=True)

    def __str__(self):
        return f'{self.author.username}: {self.challenge.title}({self.creation_date}) success[{self.success}]'

    @property
    def failures(self):
        return self.feedback.split(FEEDBACK_SEP)

    @failures.setter
    def failures(self, feedbacks):
        feedback = FEEDBACK_SEP.join(feedbacks)
        if not feedback:
            feedback = 'Ok'
        self.feedback = feedback

    @property
    def stack_traces(self):
        return self.errors.split(STACKTRACE_SEP)

    @stack_traces.setter
    def stack_traces(self, errors):
        errors = STACKTRACE_SEP.join(errors)
        if not errors:
            errors = '-'
        self.errors = errors

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

    @property
    def safe_stdouts(self):
        if self.stdouts:
            return tuple(tuple((tuple(t) + (None, None))[:2] for t in s) for s in eval(self.stdouts))
        else:
            return tuple()


class UserChallengeInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(CodingChallenge, on_delete=models.CASCADE)
    attempts = models.IntegerField(default=0)
    successful_attempts = models.IntegerField(default=0)


class UserTagInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    attempts = models.IntegerField(default=0)
    successful_attempts = models.IntegerField(default=0)
    total_challenges = models.IntegerField(default=0)
    successful_challenges = models.IntegerField(default=0)
