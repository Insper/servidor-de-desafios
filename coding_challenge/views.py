from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import FullCodingChallengeSerializer, ShortCodingChallengeSerializer
from .models import CodingChallenge


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

    def get(self, request, slug, format=None):
        try:
            challenge = CodingChallenge.objects.get(slug=slug)
            if challenge.deleted:
                raise Http404(f'There is no challenge with slug {slug}')
            serializer = FullCodingChallengeSerializer(challenge)
            return Response(serializer.data)
        except CodingChallenge.DoesNotExist:
            raise Http404(f'There is no challenge with slug {slug}')
