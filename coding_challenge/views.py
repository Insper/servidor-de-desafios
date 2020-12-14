import asyncio
from asgiref.sync import sync_to_async
from django.http import Http404
from django.core.files.base import ContentFile
from django.utils.decorators import classonlymethod
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .challenge_manager import test_code_for
from .serializers import FullCodingChallengeSerializer, ShortCodingChallengeSerializer, CodingChallengeSubmissionSerializer
from .models import CodingChallenge, CodingChallengeSubmission, user_challenge_path
from .code_runner import run_tests


class CodingChallengeListView(APIView):
    """
    List all challenges.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        challenges = CodingChallenge.objects.filter(deleted=False)
        serializer = ShortCodingChallengeSerializer(challenges, many=True)
        return Response(serializer.data)


class CodingChallengeView(APIView):
    """
    Get challenge.
    """
    permission_classes = (IsAuthenticated,)

    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    async def dispatch(self, request, *args, **kwargs):
        """
        `.dispatch()` is pretty much the same as Django's regular dispatch,
        but with extra hooks for startup, finalize, and exception handling.

        This code has been adapted to work with async from: https://github.com/encode/django-rest-framework/blob/master/rest_framework/views.py#L485
        """
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers  # deprecate?

        try:
            await sync_to_async(self.initial)(request, *args, **kwargs)

            # Get the appropriate handler method
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(),
                                  self.http_method_not_allowed)
            else:
                handler = sync_to_async(self.http_method_not_allowed)

            response = await handler(request, *args, **kwargs)

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response

    def get_or_404(self, slug):
        try:
            challenge = CodingChallenge.objects.get(slug=slug)
            if not challenge.deleted:
                return challenge
        except CodingChallenge.DoesNotExist:
            pass
        raise Http404(f'There is no challenge with slug {slug}')

    def sync_get(self, request, slug, format=None):
        challenge = self.get_or_404(slug)
        serializer = FullCodingChallengeSerializer(challenge)
        return Response(serializer.data)

    async def get(self, request, slug, format=None):
        return await sync_to_async(self.sync_get)(request, slug, format)

    def create_submission_and_serialize(self, author, challenge, result, code):
        submission = CodingChallengeSubmission.objects.create(author=author, challenge=challenge)
        submission.failures = result.failure_msgs
        submission.stack_traces = result.stack_traces
        submission.stdouts = repr(result.stdouts)
        submission.success = result.success
        submission.save()
        submission.code.save(user_challenge_path(submission, ''), ContentFile(code))

        serializer = CodingChallengeSubmissionSerializer(submission)
        return serializer.data

    async def post(self, request, slug, format=None):
        challenge = await sync_to_async(self.get_or_404)(slug)
        code = request.data.get('code')
        test_code = await sync_to_async(test_code_for)(challenge)
        result = await run_tests(code, test_code, challenge.function_name)
        data = await sync_to_async(self.create_submission_and_serialize)(request.user, challenge, result, code)
        return Response(data)
