from django.db import models
from core.models import Semester
from quiz.models import Quiz
from code_challenge.models import CodeChallenge

# Weights must always add up to exactly 100
# TODO ADD EXPLANATION TO README

class CourseGrade(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    quiz_weight = models.IntegerField(default=1)

    def __str__(self):
        return str(self.semester)


class QuizGrade(models.Model):
    course_grade = models.ForeignKey(CourseGrade, on_delete=models.CASCADE, related_name='quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    weight = models.IntegerField(default=1)  # Sum of weights of all minus one quizzes must be equal to 100
    available = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.quiz} [{self.weight}] ({self.course_grade})'


class ExamGrade(models.Model):
    course_grade = models.ForeignKey(CourseGrade, on_delete=models.CASCADE, related_name='exams')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    weight = models.IntegerField()  # Sum of weights of all exams and quiz_weight must be equal to 100
    available = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.quiz} [{self.weight}] ({self.course_grade})'


class CodeExerciseGrade(models.Model):
    course_grade = models.ForeignKey(CourseGrade, on_delete=models.CASCADE, related_name='code_exercises')
    manual_grade_weight = models.IntegerField()  # Sum of subchallenges and the manual_grade_weight must be equal to 100
    weight = models.IntegerField()  # Sum of weights of all code exercises must be equal to 100
    feedback = models.TextField(blank=True)
    available = models.BooleanField(default=False)
    name = models.CharField(max_length=1024)

    def __str__(self):
        return f'{self.name} [{self.weight}] ({self.course_grade})'


class SubChallengeGrade(models.Model):
    code_exercise = models.ForeignKey(CodeExerciseGrade, on_delete=models.CASCADE, related_name='subchallenges')
    challenge = models.ForeignKey(CodeChallenge, on_delete=models.CASCADE)
    weight = models.IntegerField()  # Sum of weights of the same CodeExerciseGrade must be equal to 100

    def __str__(self):
        return f'{self.challenge} [{self.weight}] ({self.code_exercise})'
