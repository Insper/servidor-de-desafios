from rest_framework.serializers import ModelSerializer
from .models import UserQuiz
from code_challenge.serializers import ShortCodeChallengeSerializer


class UserQuizSerializer(ModelSerializer):
    challenges = ShortCodeChallengeSerializer(read_only=True, many=True)

    class Meta:
        model = UserQuiz
        fields = ['title', 'start_time', 'submission_time', 'remaining_seconds', 'submitted', 'challenges', 'has_manual_assessment']
