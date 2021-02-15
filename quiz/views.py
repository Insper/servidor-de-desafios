from rest_framework.response import Response
from django.http import Http404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import random

from .serializers import UserQuizSerializer
from .models import QuestionTypes, Quiz, UserQuiz


class QuizView(APIView):
    """
    Get challenge.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, slug):
        try:
            quiz = Quiz.objects.get(slug=slug)
        except Quiz.DoesNotExist:
            raise Http404()

        user_quiz = None
        action = request.data.get('action')
        if action == 'start':
            try:
                user_quiz = UserQuiz.objects.get(quiz=quiz, user=request.user)
                user_quiz.submitted = user_quiz.remaining_seconds <= 0
                if user_quiz.submitted and not user_quiz.submission_time:
                    user_quiz.submission_time = timezone.now()
                elif not user_quiz.submitted:
                    user_quiz.submission_time = None
                user_quiz.save()
            except UserQuiz.DoesNotExist:
                challenges = [c for c in quiz.challenges.all()]
                if quiz.question_type == QuestionTypes.RANDOM:
                    challenges = [random.choice(challenges)]
                user_quiz = UserQuiz.objects.create(quiz=quiz, user=request.user)
                user_quiz.challenges.set(challenges)
                user_quiz.save()
        elif action == 'submit':
            try:
                user_quiz = UserQuiz.objects.get(quiz=quiz, user=request.user)
                user_quiz.submitted = True
                if not user_quiz.submission_time:
                    user_quiz.submission_time = timezone.now()
                user_quiz.save()
            except UserQuiz.DoesNotExist:
                raise Http404()
        return Response(UserQuizSerializer(user_quiz).data)


    def get(self, request, slug):
        try:
            quiz = Quiz.objects.get(slug=slug)
        except Quiz.DoesNotExist:
            raise Http404()

        try:
            user_quiz = UserQuiz.objects.get(quiz=quiz, user=request.user)
        except UserQuiz.DoesNotExist:
            raise Http404()
        if user_quiz.submitted or user_quiz.remaining_seconds <= 0:
            raise Http404()
        return Response(UserQuizSerializer(user_quiz).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_remaining_time(request, slug):
    try:
        quiz = Quiz.objects.get(slug=slug)
    except Quiz.DoesNotExist:
        raise Http404()

    try:
        user_quiz = UserQuiz.objects.get(quiz=quiz, user=request.user)
    except UserQuiz.DoesNotExist:
        raise Http404()
    return Response(user_quiz.remaining_seconds)