from django.conf import settings
from django.http import Http404
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .challenge_controller import test_code_from_slug
from .serializers import FullCodeChallengeSerializer, ShortCodeChallengeSerializer, CodeChallengeSubmissionSerializer, UserChallengeInteractionSerializer
from .models import CodeChallenge, CodeChallengeSubmission, UserChallengeInteraction, user_challenge_path
from quiz.models import UserQuiz


class CodeChallengeListView(APIView):
    """
    List all challenges.
    """
    permission_classes = (IsAuthenticated,)

    @method_decorator(cache_page(60*60*2))
    def get(self, request, format=None):
        concept_slug = request.query_params.get('concept')
        query = {
            'deleted': False,
            'published': True,
        }
        if concept_slug:
            query['concept__slug'] = concept_slug
        challenges = CodeChallenge.objects.filter(**query)
        serializer = ShortCodeChallengeSerializer(challenges, many=True)
        return Response(serializer.data)


def get_challenge_or_404(slug, user, tolerance=5 * 60):
    challenge = None
    try:
        challenge = CodeChallenge.objects.get(slug=slug)
        if not challenge.deleted and challenge.published:
            return challenge
        user_quiz = UserQuiz.objects.get(user=user, challenges__slug=slug)
        if user_quiz.remaining_seconds > -tolerance and not user_quiz.submitted:
            challenge.in_quiz = True
            return challenge
    except (CodeChallenge.DoesNotExist, UserQuiz.DoesNotExist):
        pass
    if challenge and user.is_staff:
        return challenge
    raise Http404(f'There is no challenge with slug {slug}')


class CodeChallengeView(APIView):
    """
    Get challenge.
    """
    permission_classes = (IsAuthenticated,)

    @method_decorator(cache_page(60*60*2))
    def get(self, request, slug, format=None):
        challenge = get_challenge_or_404(slug, request.user, tolerance=40)
        if 'short' in request.GET:
            serializer = ShortCodeChallengeSerializer(challenge)
        else:
            serializer = FullCodeChallengeSerializer(challenge)
        return Response(serializer.data)

    def post(self, request, slug, format=None):
        challenge = get_challenge_or_404(slug, request.user)
        code = request.data.get('code')
        result = request.data.get('result')
        submission = CodeChallengeSubmission(author=request.user, challenge=challenge)
        submission.failures = result['failure_msgs']
        submission.stack_traces = result['stack_traces']
        submission.stdouts = [
                [{
                    'output': line[0] if len(line) else None,
                    'input': line[1] if len(line) > 1 else None
                } for line in test_case
            ] for test_case in result['stdouts']]
        submission.success = result['success']
        submission.save()
        submission.code.save(user_challenge_path(submission, ''), ContentFile(code))

        serializer = CodeChallengeSubmissionSerializer(submission)
        return Response(serializer.data)


class CodeChallengeSubmissionListView(APIView):
    """
    List all submissions.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, slug, format=None):
        submissions = CodeChallengeSubmission.objects.filter(author=request.user, challenge__slug=slug).order_by('-creation_date')
        serializer = CodeChallengeSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_submission(request, slug, submission_id):
    query_args = {
        'id': submission_id,
        'challenge__slug': slug,
    }
    if not request.user.is_superuser:
        query_args['author__id'] = request.user.id
    try:
        submission = CodeChallengeSubmission.objects.get(**query_args)
    except CodeChallengeSubmission.DoesNotExist:
        raise Http404()
    return Response(CodeChallengeSubmissionSerializer(submission).data)


class CodeChallengeSubmissionCodeView(APIView):
    """
    Get challenge submission code.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, slug, submission_id, format=None):
        query_args = {
            'id': submission_id,
            'challenge__slug': slug,
        }
        if not request.user.is_superuser:
            query_args['author__id'] = request.user.id
        try:
            submission = CodeChallengeSubmission.objects.get(**query_args)
            return Response({'code': submission.code.read().decode('utf-8')})
        except CodeChallengeSubmission.DoesNotExist:
            raise Http404('This submission does not exist')


class CodeInteractionListView(APIView):
    """
    List all user-code interactions for this user.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        selected_username = request.GET.get('username')
        if selected_username and request.user.is_staff:
            interactions = UserChallengeInteraction.objects.filter(user__username=selected_username)
        else:
            interactions = UserChallengeInteraction.objects.filter(user=request.user)
        serializer = UserChallengeInteractionSerializer(interactions, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_interactions_for(request):
    usernames = request.GET.get('usernames').split(',')
    challenge_slugs = request.GET.get('challenges').split(',')

    interactions = UserChallengeInteraction.objects.filter(user__username__in=usernames, challenge__slug__in=challenge_slugs)
    serializer = UserChallengeInteractionSerializer(interactions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_page(60*60*2)
def get_test_code(request, slug):
    test_code = None
    if request.GET.get('token') == settings.BACKEND_TOKEN:
        test_code = test_code_from_slug(slug)
    return Response(test_code)
