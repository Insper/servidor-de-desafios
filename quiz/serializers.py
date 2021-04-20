from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Quiz, UserQuiz, QuizChallengeFeedback
from core.serializers import UserSerializer
from code_challenge.serializers import ShortCodeChallengeSerializer, CodeChallengeSubmissionSerializer


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
        fields = ['title', 'user', 'start_time', 'submission_time', 'remaining_seconds', 'duration', 'submitted', 'challenges', 'has_manual_assessment', 'slug']


class QuizChallengeFeedbackSerializer(ModelSerializer):
    user = UserSerializer()
    challenge_slug = SerializerMethodField()
    submission_id = SerializerMethodField()
    quiz_slug = SerializerMethodField()

    def get_challenge_slug(self, obj):
        return obj.challenge.slug

    def get_submission_id(self, obj):
        return obj.submission_id

    def get_quiz_slug(self, obj):
        return obj.quiz.slug

    class Meta:
        model = QuizChallengeFeedback
        fields = ['id', 'user', 'quiz_slug', 'challenge_slug', 'submission_id', 'auto_grade', 'manual_grade', 'graded', 'feedback']
