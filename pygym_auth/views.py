import secrets
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import update_session_auth_hash
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from django.conf import settings
from core.models import PyGymUser, EmailToken


SUCCESS = 0
WRONG_PASSWORD = 1
PASSWORDS_DONT_MATCH = 2
OLD_NEW_PASSWORDS_EQUAL = 3
INVALID_EMAIL_DOMAIN = 4
USER_EXISTS = 5
OTHER_ERROR = 10


@api_view(['POST'])
def signup(request):
    if request.data.get('token') != settings.BACKEND_TOKEN:
        raise PermissionDenied()

    first_name = request.data.get('first_name', '').strip()
    last_name = request.data.get('last_name', '').strip()
    email = request.data.get('email', '').strip()
    username = email[:email.find('@')]
    password = request.data.get('password', '')

    if not email.endswith('insper.edu.br'):
        return Response({'code': INVALID_EMAIL_DOMAIN})

    user_exists = PyGymUser.objects.filter(username=username).exists()
    if user_exists and Token.objects.filter(user__username=username).exists():
        return Response({'code': USER_EXISTS})
    if not first_name or not last_name or not password or '@' not in email:
        return Response({'code': OTHER_ERROR})

    if user_exists:
        new_user = PyGymUser.objects.get(username=username)
        new_user.email = email
        new_user.set_password(password)
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()
    else:
        new_user = PyGymUser.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
    EmailToken.objects.filter(user=new_user).delete()
    email_token = EmailToken.objects.create(user=new_user, token=secrets.token_urlsafe(20)[:16])

    send_mail(
        'Verificação de e-mail: Servidor de Design de Software',
        '''Olá {nome},

Foi realizada uma solicitação de criação de conta no servidor de Design de Software para o e-mail {email}. Caso tenha ocorrido um engano, basta desconsiderar este e-mail.

Para concluir seu cadastro, clique no link a seguir:

{link}

O seu login de usuário é: {username}

Este é um e-mail enviado automaticamente, por favor, não responda.
'''.format(
            nome=first_name,
            email=email,
            link='{base}auth/confirm/?token={token}'.format(base=settings.FRONTEND_URL, token=email_token.token),
            username=username,
        ),
        'softdes.insper@gmail.com',
        [email],
        fail_silently=False,
    )
    return Response({'code': SUCCESS})


@api_view(['POST'])
def email_confirmation(request):
    if request.data.get('token') != settings.BACKEND_TOKEN:
        raise PermissionDenied()

    email_token = request.data.get('user_token')
    if not email_token:
        return Response({'confirmed': False, 'msg': 'missing token'})

    try:
        stored_token = EmailToken.objects.get(token=email_token)

        Token.objects.get_or_create(user=stored_token.user)

    except EmailToken.DoesNotExist:
        return Response({'confirmed': False, 'msg': 'token does not exist'})
    return Response({'confirmed': True, 'msg': 'ok'})


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
