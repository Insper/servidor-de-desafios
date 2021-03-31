from rest_framework.response import Response
from django.http import Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .serializers import UserSerializer, UserTagSerializer, ConceptSerializer
from .models import Concept, PyGymUser, UserTag


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    return Response(UserSerializer(request.user).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_users(request):
    users = PyGymUser.objects.all()
    return Response(UserSerializer(users, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_user_tags(request):
    tags = UserTag.objects.all()
    return Response(UserTagSerializer(tags, many=True).data)


class ConceptListView(APIView):
    """
    List all Concepts.
    """
    permission_classes = (IsAuthenticated,)

    @method_decorator(cache_page(60*60*2))
    def get(self, request, format=None):
        concepts = Concept.objects.order_by('order')
        serializer = ConceptSerializer(concepts, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_page(60*60*2)
def get_concept(request, slug):
    try:
        concept = Concept.objects.get(slug=slug)
    except Concept.DoesNotExist:
        raise Http404(f'Concept {slug} does not exist')
    return Response(ConceptSerializer(concept).data)
