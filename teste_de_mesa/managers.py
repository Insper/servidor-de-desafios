from django.db import models
from django.utils import timezone

from core.choices import Resultado


class InteracaoUsuarioPassoTesteDeMesaQuerySet(models.QuerySet):
    def do_usuario(self, usuario):
        return self.filter(interacao__usuario=usuario)

    def do_teste(self, teste_de_mesa):
        return self.filter(interacao__exercicio=teste_de_mesa)

    def passo_atual(self, usuario, teste_de_mesa):
        interacoes = self.do_usuario(usuario).do_teste(teste_de_mesa)
        passo_max = interacoes.aggregate(models.Max('passo'))
        ultimo_passo = passo_max['passo__max']
        if ultimo_passo is None:
            return 0
        ultima_interacao = interacoes.get(passo=ultimo_passo)
        if ultima_interacao.melhor_resultado == Resultado.OK:
            return ultimo_passo + 1
        return ultimo_passo


InteracaoUsuarioPassoTesteDeMesaManager = InteracaoUsuarioPassoTesteDeMesaQuerySet.as_manager
