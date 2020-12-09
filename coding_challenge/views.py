from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import FullCodingChallengeSerializer, ShortCodingChallengeSerializer
from .models import CodingChallenge


class CodingChallengeList(APIView):
    """
    List all challenges.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        challenges = CodingChallenge.objects.all()
        serializer = ShortCodingChallengeSerializer(challenges, many=True)
        return Response(serializer.data)


