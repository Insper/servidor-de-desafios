from django.db import models
from django.contrib.auth.models import User
from enum import Enum


FEEDBACK_SEP = '|||'


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
    function_name = models.CharField(max_length=50, blank=False)

    @property
    def full_title(self):
        title = 'Desafio {0}'.format(self.id)
        if self.title:
            title += ': {0}'.format(self.title)
        return title

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


def escape_js(string):
    replacements = {
        '\n': '\\n',
        '\r': '',
        '"': '\"',
    }
    for k, v in replacements.items():
        string = string.replace(k, v)
    return string


class ChallengeSubmission(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField('date created', auto_now_add=True)
    feedback = models.TextField(blank=True)
    code = models.FileField(upload_to=user_directory_path)
    result = models.CharField(max_length=5, choices=[(res, res.value) for res in Result], blank=True)

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
    def clean_failure_list(self):
        return list(set(self.failure_list))

    @classmethod
    def submissions_by_challenge(cls, author):
        user_submissions = ChallengeSubmission.objects.filter(author=author)
        challenge2submissions = {}
        for sub in user_submissions:
            if sub.challenge in challenge2submissions:
                sbc = challenge2submissions[sub.challenge]
                if sub.result == str(Result.OK):
                    sbc.best_result = str(Result.OK)
                sbc.submissions.append(sub)
            else:
                challenge2submissions[sub.challenge] = SubmissionsByChallenge(sub.challenge, [sub], sub.result)
        return list(challenge2submissions.values())

    @classmethod
    def latest_submission(cls, challenge, author):
        latest = ChallengeSubmission.objects.filter(challenge=challenge, author=author).latest('created')
        source_code = ''
        if latest:
            source_code = latest.code.read().decode('utf-8')
        return escape_js(source_code)
