from rest_framework.serializers import ModelSerializer
from .models import Quiz, UserQuiz
from core.serializers import UserSerializer
from code_challenge.serializers import ShortCodeChallengeSerializer


class QuizSerializer(ModelSerializer):
    challenges = ShortCodeChallengeSerializer(read_only=True, many=True)

    class Meta:
        model = Quiz
        fields = [
            'title',
            'question_type',
            'slug',
            'duration',
            'deadline',
            'challenges',
            'has_manual_assessment',
        ]


class UserQuizSerializer(ModelSerializer):
    user = UserSerializer()
    challenges = ShortCodeChallengeSerializer(read_only=True, many=True)

    class Meta:
        model = UserQuiz
        fields = ['title', 'user', 'start_time', 'submission_time', 'remaining_seconds', 'submitted', 'challenges', 'has_manual_assessment', 'slug']
