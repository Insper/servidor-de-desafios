from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RespostaExProgramacao, InteracaoUsarioExercicio
from .choices import Resultado


@receiver(post_save, sender=RespostaExProgramacao)
def post_resposta_save(sender, instance, created, raw, using, update_fields,
                       **kwargs):
    autor = instance.autor
    exercicio = instance.exercicio
    try:
        interacao = InteracaoUsarioExercicio.objects.get(exercicio=exercicio,
                                                         usuario=autor)
    except InteracaoUsarioExercicio.DoesNotExist:
        interacao = InteracaoUsarioExercicio.objects.create(
            exercicio=exercicio, usuario=autor)
    if created:
        interacao.tentativas += 1
    if instance.resultado == Resultado.OK:
        interacao.melhor_resultado = Resultado.OK
    interacao.ultima_submissao = instance
    interacao.save()
