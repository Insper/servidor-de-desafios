from rest_framework.response import Response
from django.http import Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .serializers import UserSerializer, ConceptSerializer
from .models import Concept


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    return Response(UserSerializer(request.user).data)


class ConceptListView(APIView):
    """
    List all Concepts.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        concepts = Concept.objects.order_by('order')
        serializer = ConceptSerializer(concepts, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_concept(request, slug):
    try:
        concept = Concept.objects.get(slug=slug)
    except Concept.DoesNotExist:
        raise Http404(f'Concept {slug} does not exist')
    return Response(ConceptSerializer(concept).data)
