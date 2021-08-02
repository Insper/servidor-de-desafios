from django.contrib import admin
from .models import Quiz, UserQuiz, QuizChallengeFeedback


class QuizChallengeFeedbackAdmin(admin.ModelAdmin):
    readonly_fields = ["quiz", "challenge", "submission"]


admin.site.register(Quiz)
admin.site.register(UserQuiz)
admin.site.register(QuizChallengeFeedback, QuizChallengeFeedbackAdmin)
