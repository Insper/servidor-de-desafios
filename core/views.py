from rest_framework.response import Response
from django.contrib.auth import update_session_auth_hash
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer


SUCCESS = 0
WRONG_PASSWORD = 1
PASSWORDS_DONT_MATCH = 2
OLD_NEW_PASSWORDS_EQUAL = 3


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
