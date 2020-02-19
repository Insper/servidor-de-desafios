from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RespostaTesteDeMesa, InteracaoUsuarioPassoTesteDeMesa
from core.models import InteracaoUsarioExercicio
from core.choices import Resultado


@receiver(post_save, sender=RespostaTesteDeMesa)
def post_resposta_save(sender, instance, created, raw, using, update_fields,
                       **kwargs):
    autor = instance.autor
    exercicio = instance.exercicio
    passo = instance.passo
    try:
        interacao = InteracaoUsarioExercicio.objects.get(exercicio=exercicio,
                                                         usuario=autor)
        interacao_passo = InteracaoUsuarioPassoTesteDeMesa.objects.get(
            interacao=interacao, passo=passo)
    except InteracaoUsarioExercicio.DoesNotExist:
        interacao = InteracaoUsarioExercicio.objects.create(
            exercicio=exercicio, usuario=autor)
        interacao_passo = InteracaoUsuarioPassoTesteDeMesa.objects.create(
            interacao=interacao, passo=passo)
    except InteracaoUsuarioPassoTesteDeMesa.DoesNotExist:
        interacao_passo = InteracaoUsuarioPassoTesteDeMesa.objects.create(
            interacao=interacao, passo=passo)
    if created:
        interacao.tentativas += 1
        interacao_passo.tentativas += 1
    if instance.resultado == Resultado.OK:
        interacao_passo.melhor_resultado = Resultado.OK
        if passo == len(exercicio.especifico().gabarito_list) - 1:
            interacao.melhor_resultado = Resultado.OK
    interacao.ultima_submissao = instance
    interacao_passo.ultima_submissao = instance
    interacao.save()
    interacao_passo.save()
