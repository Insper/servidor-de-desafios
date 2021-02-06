from rest_framework.response import Response
from django.contrib.auth import update_session_auth_hash
from django.http import Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .serializers import UserSerializer, ConceptSerializer
from .models import Concept


SUCCESS = 0
WRONG_PASSWORD = 1
PASSWORDS_DONT_MATCH = 2
OLD_NEW_PASSWORDS_EQUAL = 3


@api_view(['POST'])
def login_with_credentials(request):
    login = request.data.get('login')
    password = request.data.get('password')
    return Response(login, password)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    return Response(UserSerializer(request.user).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    pass_data = request.data
    old_password = pass_data['oldPassword']
    new_password = pass_data['newPassword']
    repeat_password = pass_data['repeatPassword']
    user = request.user

    if not user.check_password(old_password):
        return Response({'code': WRONG_PASSWORD})
    if new_password != repeat_password:
        return Response({'code': PASSWORDS_DONT_MATCH})
    if old_password == new_password:
        return Response({'code': OLD_NEW_PASSWORDS_EQUAL})
    user.set_password(new_password)
    user.save()
    update_session_auth_hash(request, user)
    return Response({'code': SUCCESS})


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
