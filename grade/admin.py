from io import TextIOWrapper
from django.contrib import admin
from django.forms import ModelForm, FileField
from .models import CourseGrade, QuizGrade, ExamGrade, CodeExerciseGrade, SubChallengeGrade, CodeExerciseFeedback, SubChallengeGrade


class QuizGradeInline(admin.TabularInline):
    model = QuizGrade
    extra = 0


class ExamGradeInline(admin.TabularInline):
    model = ExamGrade
    extra = 0


class CodeExerciseGradeInline(admin.TabularInline):
    model = CodeExerciseGrade
    extra = 0


class CourseGradeAdmin(admin.ModelAdmin):
    inlines = (QuizGradeInline, ExamGradeInline, CodeExerciseGradeInline)


admin.site.register(CourseGrade, CourseGradeAdmin)
admin.site.register(CodeExerciseFeedback)
admin.site.register(SubChallengeGrade)
