from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import TraceChallenge
from .serializers import ShortTraceChallengeSerializer, FullTraceChallengeSerializer
from .trace_controller import states_for


class TraceChallengeListView(APIView):
    """
    List all challenges.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        challenges = TraceChallenge.objects.filter(deleted=False, published=True)
        serializer = ShortTraceChallengeSerializer(challenges, many=True)
        return Response(serializer.data)


def get_challenge_or_404(slug):
    try:
        challenge = TraceChallenge.objects.get(slug=slug)
        if not challenge.deleted and challenge.published:
            return challenge
    except TraceChallenge.DoesNotExist:
        pass
    raise Http404(f'There is no trace with slug {slug}')


class TraceChallengeView(APIView):
    """
    Get challenge.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, slug, format=None):
        challenge = get_challenge_or_404(slug)
        serializer = FullTraceChallengeSerializer(challenge)
        return Response(serializer.data)


class TraceStateListView(APIView):
    """
    List all states already completed by the user.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, slug, format=None):
        trace = get_challenge_or_404(slug)
        states = states_for(trace)
        return Response({
            'states': states,
            'totalStates': len(states),
        })
