from django.db import models
from django.conf import settings
from code_challenge.models import CodeChallenge, CodeChallengeSubmission
from django.utils import timezone
import secrets


def create_slug():
    return secrets.token_urlsafe(8)


class QuestionTypes(models.TextChoices):
    ALL = 'AL', 'all'
    RANDOM = 'RD', 'random'


class Quiz(models.Model):
    title = models.CharField(max_length=1024)
    question_type = models.CharField(
        max_length=2,
        choices=QuestionTypes.choices,
        default=QuestionTypes.ALL
    )
    slug = models.SlugField(default=create_slug)
    duration = models.PositiveIntegerField()
    deadline = models.DateTimeField()
    challenges = models.ManyToManyField(CodeChallenge)
    has_manual_assessment = models.BooleanField(default=False)
    grading_started = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} [{self.duration} min] ({self.slug})'


class UserQuiz(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    submission_time = models.DateTimeField(blank=True, null=True)
    submitted = models.BooleanField(default=False)
    challenges = models.ManyToManyField(CodeChallenge)

    @property
    def title(self):
        return self.quiz.title

    @property
    def remaining_seconds(self):
        base_duration = self.quiz.duration
        additional_time = max(
            self.user.additional_quiz_time_percent * base_duration,
            self.user.additional_quiz_time_absolute
        )
        deadline = self.quiz.deadline + timezone.timedelta(minutes=additional_time)
        ellapsed = (timezone.now() - self.start_time).total_seconds()
        return round(min(
            (deadline - self.start_time).total_seconds(),
            (base_duration + additional_time) * 60
        ) - ellapsed)

    @property
    def duration(self):
        return self.quiz.duration

    @property
    def slug(self):
        return self.quiz.slug

    @property
    def has_manual_assessment(self):
        return self.quiz.has_manual_assessment

    def __str__(self):
        return f'{self.user} - {self.quiz}'


class QuizChallengeFeedback(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(CodeChallenge, on_delete=models.CASCADE)
    submission = models.ForeignKey(CodeChallengeSubmission, on_delete=models.CASCADE, null=True)
    auto_grade = models.FloatField(default=0)
    manual_grade = models.FloatField(null=True)
    feedback = models.TextField(blank=True)

    @property
    def grade(self):
        return self.auto_grade + (self.manual_grade if self.manual_grade else 0)

    @property
    def graded(self):
        return self.manual_grade is not None

    def __str__(self):
        return f'{self.user} - {self.quiz} - {self.challenge}'
