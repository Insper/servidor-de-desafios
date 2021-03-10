from django.contrib import admin
from .models import Quiz, UserQuiz, QuizChallengeFeedback


admin.site.register(Quiz)
admin.site.register(UserQuiz)
admin.site.register(QuizChallengeFeedback)
