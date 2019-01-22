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
    return 'upload/user_{0}/{1}'.format(instance.author.username, filename)

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