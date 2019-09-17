from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from enum import Enum
import markdown
from collections import namedtuple, defaultdict


FEEDBACK_SEP = '|||'
STACKTRACE_SEP = '<|>|<|>'
STACKTRACE_FILE_PATTERN = 'File "<string>", '


class Result(Enum):
    def __str__(self):
        return str(self.value)

    ERROR = "Erro"
    OK = "OK"

class Challenge(models.Model):
    release = models.DateTimeField('date released', auto_now=True)
    expire = models.DateTimeField('date expired', blank=True, null=True)
    title = models.CharField(max_length=1024, blank=True)
    problem = models.TextField(blank=False)
    test_file = models.FileField(upload_to='challenge_tests/')
    function_name = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='challenge/', blank=True)
    published = models.BooleanField(default=True)
    tags = TaggableManager()

    @classmethod
    def all_published(cls):
        return Challenge.objects.filter(published=True)

    @property
    def full_title(self):
        title = '{0}'.format(self.id)
        if self.title:
            title += ': {0}'.format(self.title)
        return title

    @property
    def html_problem(self):
        return markdown.markdown(self.problem, extensions=['extra', 'codehilite'])

    def __str__(self):
        return self.full_title


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'upload/user_{0}/ch{1}_{2}.py'.format(instance.author.username, instance.challenge.id, instance.created.strftime('%Y_%m_%d_%H_%M_%S_%f'))


class SubmissionsByChallenge:
    def __init__(self, challenge, submissions, best_result):
        self.challenge = challenge
        self.submissions = submissions
        self.best_result = best_result

    @property
    def attempts(self):
        return len(self.submissions)

    @property
    def latest_submission(self):
        return sorted(self.submissions, key=lambda s: s.created)[-1]


def escape_js(string):
    replacements = {
        '\n': '\\n',
        '\r': '',
        '"': '\\\"',
    }
    for k, v in replacements.items():
        string = string.replace(k, v)
    return string


ErrorData = namedtuple('ErrorData', 'message, stacktrace')


class ChallengeSubmissionManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.author = None
        return super().__init__(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(deleted=False)
        if self.author is not None:
            queryset = queryset.filter(author=self.author)
        return queryset

    def by(self, author):
        self.author = author
        return self

    def count_challenges_per_day(self, start=None, end=None):
        all_submissions = self.get_queryset()
        challenges_per_day = defaultdict(lambda: set())
        for submission in all_submissions:
            if (start and submission.created.date() < start) or (end and submission.created.date() > end):
                continue
            challenges_per_day[submission.created.date()].add(submission.challenge_id)
        per_day = defaultdict(lambda: 0)
        per_day.update({d: len(c) for d, c in challenges_per_day.items()})
        return per_day

    def latest_submission(self, challenge):
        all_submissions = self.get_queryset().filter(challenge=challenge)
        if not all_submissions:
            return ''
        latest = all_submissions.latest('created')
        source_code = ''
        if latest:
            try:
                source_code = latest.code.read().decode('utf-8')
            except:
                source_code = ''
        return escape_js(source_code)

    def submissions_by_challenge(self, challenge_ids=None):
        user_submissions = self.get_queryset().all()
        if self.author and self.author.is_staff:
            challenges = Challenge.objects.all()
        else:
            challenges = Challenge.all_published()
        challenge2submissions = {ch: SubmissionsByChallenge(ch, [], str(Result.ERROR)) for ch in challenges if challenge_ids is None or ch.id in challenge_ids}
        for sub in user_submissions:
            if challenge_ids is None or sub.challenge.id in challenge_ids:
                if sub.challenge in challenge2submissions:
                    sbc = challenge2submissions[sub.challenge]
                    if sub.result == str(Result.OK):
                        sbc.best_result = str(Result.OK)
                    sbc.submissions.append(sub)
                else:
                    challenge2submissions[sub.challenge] = SubmissionsByChallenge(sub.challenge, [sub], sub.result)
        return sorted(list(challenge2submissions.values()), key=lambda s: s.challenge.id)


class ChallengeSubmission(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField('date created', auto_now_add=True)
    feedback = models.TextField(blank=True)
    errors = models.TextField(blank=True)
    code = models.FileField(upload_to=user_directory_path)
    result = models.CharField(max_length=5, choices=[(res, res.value) for res in Result], blank=True)
    deleted = models.BooleanField(default=False)

    objects_with_deleted = models.Manager() # Include all objects, even the ones marked with soft delete.
    objects = ChallengeSubmissionManager() # Only objects that were not soft deleted.

    def __str__(self):
        return '{0}: Challenge {1} - date[{2}] result[{3}]'.format(self.author.username, self.challenge.id, self.created, self.result)

    @property
    def failure_list(self):
        return self.feedback.split(FEEDBACK_SEP)

    @failure_list.setter
    def failure_list(self, feedback_list):
        feedback = FEEDBACK_SEP.join(feedback_list)
        if not feedback:
            feedback = 'Sem erros.'
        self.feedback = feedback

    @property
    def stack_traces(self):
        return self.errors.split(STACKTRACE_SEP)

    @stack_traces.setter
    def stack_traces(self, error_list):
        errors = STACKTRACE_SEP.join(error_list)
        if not errors:
            errors = '-'
        self.errors = errors

    @property
    def clean_stack_traces(self):
        retval = []
        for st in self.stack_traces:
            clean = st
            if 'AssertionError' in clean:
                clean = 'Resposta diferente da esperada.'
            else:
                start = clean.rfind(STACKTRACE_FILE_PATTERN)
                if start >= 0:
                    clean = clean[start + len(STACKTRACE_FILE_PATTERN):]
            clean = clean.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>').replace(' ', '&nbsp;')
            retval.append(clean)
        return retval

    @property
    def clean_feedback(self):
        msgs = self.failure_list
        stacktraces = ['' for _ in msgs]
        sts = self.clean_stack_traces
        stacktraces[:len(sts)] = sts
        return list(set([ErrorData(msg, st) for msg, st in zip(msgs, stacktraces)]))

