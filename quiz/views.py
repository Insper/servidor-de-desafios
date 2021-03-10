from code_challenge.models import CodeChallengeSubmission
from rest_framework.response import Response
from django.http import Http404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
import random

from .serializers import QuizSerializer, UserQuizSerializer, QuizChallengeFeedbackSerializer
from .models import QuestionTypes, Quiz, QuizChallengeFeedback, UserQuiz


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_quizzes(request):
    quizzes = Quiz.objects.all()
    return Response(QuizSerializer(quizzes, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_user_quizzes(request, slug):
    try:
        quiz = Quiz.objects.get(slug=slug)
    except Quiz.DoesNotExist:
        raise Http404()

    user_quizzes = UserQuiz.objects.filter(quiz=quiz)
    return Response(UserQuizSerializer(user_quizzes, many=True).data)



@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def quiz_details(request, slug):
    try:
        quiz = Quiz.objects.get(slug=slug)
        return Response(QuizSerializer(quiz).data)
    except Quiz.DoesNotExist:
        raise Http404()



@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def start_grading_quiz(request, slug):
    try:
        quiz = Quiz.objects.get(slug=slug)
    except Quiz.DoesNotExist:
        raise Http404()

    challenges = quiz.challenges.all()
    all_submissions = CodeChallengeSubmission.objects.filter(challenge__in=challenges)
    user_challenges = {}
    for submission in all_submissions:
        user_challenges.setdefault(
            submission.author.id, {}
        ).setdefault(
            submission.challenge.slug, []
        ).append(submission)

    total_challenges = len(challenges)
    if quiz.question_type == QuestionTypes.RANDOM:
        total_challenges = 1

    feedback_list = []
    for user_quiz in UserQuiz.objects.filter(quiz=quiz):
        user = user_quiz.user
        for challenge in challenges:
            submissions = user_challenges.get(user.id, {}).get(challenge.slug, [])
            submissions.sort(key=lambda sub: sub.creation_date)

            try:
                feedback = QuizChallengeFeedback.objects.get(quiz=quiz, user=user, challenge=challenge)
            except QuizChallengeFeedback.DoesNotExist:
                feedback = QuizChallengeFeedback.objects.create(quiz=quiz, user=user, challenge=challenge)
                auto_grade = 10 / total_challenges
                if quiz.has_manual_assessment:
                    auto_grade *= 0.4
                if submissions and submissions[-1].success:
                    feedback.auto_grade = auto_grade
                else:
                    feedback.auto_grade = 0

                feedback.submissions.set(submissions)
                feedback.save()

            feedback_list.append(feedback)

    return Response(QuizChallengeFeedbackSerializer(feedback_list, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def post_challenge_grade(request, slug, challenge_slug):
    username = request.data.get('username')
    auto_grade = request.data.get('auto_grade')
    manual_grade = request.data.get('manual_grade')
    feedback = request.data.get('feedback')

    if not username:
        raise Http404()

    try:
        challenge_feedback = QuizChallengeFeedback.objects.get(quiz__slug=slug, user__username=username, challenge__slug=challenge_slug)
    except QuizChallengeFeedback.DoesNotExist:
        raise Http404()

    if auto_grade is not None:
        challenge_feedback.auto_grade = auto_grade
    if manual_grade is not None:
        challenge_feedback.manual_grade = manual_grade
    if feedback is not None:
        challenge_feedback.feedback = feedback
    challenge_feedback.save()

    return Response(QuizChallengeFeedbackSerializer(challenge_feedback).data)


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
        quiz = None
        if slug != 'current':
            try:
                quiz = Quiz.objects.get(slug=slug)
            except Quiz.DoesNotExist:
                raise Http404()

        try:
            if quiz:
                user_quiz = UserQuiz.objects.get(quiz=quiz, user=request.user)
            else:
                user_quiz = UserQuiz.objects.filter(user=request.user, submitted=False).latest('start_time')
        except UserQuiz.DoesNotExist:
            raise Http404()
        if not user_quiz or user_quiz.submitted or user_quiz.remaining_seconds <= 0:
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
