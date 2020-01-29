from django.db import models


class Resultado(models.TextChoices):
    ERRO = 'ER', 'Erro'
    OK = 'OK', 'OK'
