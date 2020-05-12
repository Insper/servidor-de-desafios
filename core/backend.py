from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import Usuario
from django.conf import settings


class CustomerBackend(ModelBackend):

    def authenticate(self, request, **kwargs):
        user = kwargs['username']
        password = kwargs['password']
        senha_prova = kwargs['senha_prova']
        if settings.MODO_PROVA and settings.SENHA_PROVA == senha_prova:
            return None
        try:
            usuario = Usuario.objects.get(username=user)
            if usuario.check_password(password) is True:
                return usuario
        except Usuario.DoesNotExist:
            pass