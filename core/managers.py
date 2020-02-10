from django.db import models
from django.utils import timezone
import inspect

from .models_helper import escape_js
from .date_utils import DateRange
from collections import defaultdict
from .choices import Resultado


class ExercicioQuerySet(models.QuerySet):
    def ordenados(self):
        return self.order_by('id')

    def publicados(self):
        return self.filter(publicado=True)

    def disponiveis_para(self, usuario):
        if usuario.is_staff:
            return self
        ids = usuario.exercicios_programados_disponiveis().values_list(
            'exercicio', flat=True)
        return self.filter(id__in=ids)

    def disponivel_para(self, exercicio, usuario):
        return exercicio in self.disponiveis_para(usuario)

    def carrega_para(self, exercicio_id, usuario):
        exercicio = None
        try:
            exercicio = self.get(pk=exercicio_id)
            if not self.disponivel_para(exercicio, usuario):
                return None
        except self.model.DoesNotExist:
            return None
        return exercicio.especifico()


ExercicioManager = ExercicioQuerySet.as_manager


class ExercicioProgramadoQuerySet(models.QuerySet):
    def disponiveis_para(self, usuario):
        if usuario.is_staff:
            return self
        turmas_ids = [t.id for t in usuario.turmas_atuais()]
        agora = timezone.now()
        hoje = agora.date()
        q_inicio = models.Q(inicio__isnull=True) | models.Q(inicio__lte=hoje)
        q_fim = models.Q(fim__isnull=True) | models.Q(fim__gt=hoje)
        return self.filter(q_inicio & q_fim,
                           turma__id__in=turmas_ids,
                           exercicio__publicado=True)


ExercicioProgramadoManager = ExercicioProgramadoQuerySet.as_manager


class RespostaExProgramacaoManager(models.Manager):
    class SubmissoesPorExercicio:
        def __init__(self,
                     exercicio,
                     submissoes=None,
                     melhor_resultado='Erro'):
            if submissoes is None:
                submissoes = []
            self.exercicio = exercicio
            self.submissoes = submissoes
            self.melhor_resultado = melhor_resultado

        @property
        def tentativas(self):
            return len(self.submissoes)

        @property
        def ultima_submissao(self):
            return sorted(self.submissoes, key=lambda s: s.data_submissao)[-1]

    def __init__(self, *args, incluir_deletados=False, **kwargs):
        self.autor = None
        self.incluir_deletados = incluir_deletados
        return super().__init__(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.incluir_deletados:
            queryset = queryset.filter(deletado=False)
        if self.autor is not None:
            queryset = queryset.filter(autor=self.autor)
        return queryset

    def por(self, autor):
        self.autor = autor
        return self

    def conta_exercicios_por_dia(self, inicio=None, fim=None):
        todas_submissoes = self.get_queryset()
        exercicios_por_dia = defaultdict(lambda: set())
        for submissao in todas_submissoes:
            ds = submissao.data_submissao.date()
            if (inicio and ds < inicio) or (fim and ds > fim):
                continue
            exercicios_por_dia[ds].add(submissao.exercicio_id)
        por_dia = defaultdict(lambda: 0)
        por_dia.update({d: len(c) for d, c in exercicios_por_dia.items()})
        return por_dia

    def ultima_submissao(self, exercicio):
        todas_submissoes = self.get_queryset().filter(exercicio=exercicio)
        if not todas_submissoes:
            return ''
        ultima = todas_submissoes.latest('data_submissao')
        source_code = ''
        if ultima:
            try:
                fonte = ultima.codigo.read().decode('utf-8')
            except:
                fonte = ''
        return escape_js(fonte)

    def respostas_por_exercicio(self, exercicios):
        todas_submissoes = self.get_queryset().all()
        exercicio2submissao = {
            ex: RespostaExProgramacaoManager.SubmissoesPorExercicio(ex)
            for ex in exercicios
        }
        for sub in todas_submissoes:
            spe = exercicio2submissao.setdefault(
                sub.exercicio,
                RespostaExProgramacaoManager.SubmissoesPorExercicio(
                    sub.exercicio))
            if sub.resultado == Resultado.OK:
                spe.melhor_resultado = Resultado.OK.label
            spe.submissoes.append(sub)
        return sorted(list(exercicio2submissao.values()),
                      key=lambda s: s.exercicio.id)


class ProvaQuerySet(models.QuerySet):
    def disponiveis_para(self, usuario):
        if usuario.is_staff:
            return self
        turmas = usuario.matricula_set.values_list('turma', flat=True)
        now = timezone.now()
        return self.filter(models.Q(inicio__lte=now) & models.Q(fim__gte=now),
                           turma__in=turmas)


ProvaManager = ProvaQuerySet.as_manager


class TurmaQuerySet(models.QuerySet):
    def get_date_range(self, usuario):
        turmas = self.filter(matricula__aluno__id=usuario.id)
        hoje = timezone.now().date()
        inicio = None
        for t in turmas:
            if t.inicio and t.fim and t.inicio <= hoje and hoje <= t.fim:
                if inicio is None or t.inicio < inicio:
                    inicio = t.inicio
        return DateRange(inicio, hoje)

    def do_aluno(self, usuario):
        return self.filter(matricula__aluno__id=usuario.id)

    def atuais(self):
        agora = timezone.now()
        hoje = agora.date()
        q_inicio = models.Q(inicio__isnull=True) | models.Q(inicio__lte=hoje)
        q_fim = models.Q(fim__isnull=True) | models.Q(fim__gt=hoje)
        return self.filter(q_inicio & q_fim)


TurmaManager = TurmaQuerySet.as_manager


class InteracaoMock:
    def __init__(self, exercicio, tentativas, melhor_resultado,
                 ultima_submissao):
        self.exercicio = exercicio
        self.tentativas = tentativas
        self.melhor_resultado = melhor_resultado
        self.ultima_submissao = ultima_submissao


class InteracaoUsarioExercicioQuerySet(models.QuerySet):
    def submissoes_por_usuario(self, usuarios):
        usuario2interacao = {u.id: {} for u in usuarios}
        for interacao in self:
            uid = interacao.usuario_id
            eid = interacao.exercicio_id
            if uid in usuario2interacao:
                usuario2interacao[uid][eid] = interacao
        return usuario2interacao

    def por(self, usuario):
        return self.filter(usuario=usuario)

    def agrupado_por(self, exercicios):
        exercicio2submissao = {
            ex.id: InteracaoMock(ex, 0, Resultado.ERRO, None)
            for ex in exercicios
        }
        exercicio2submissao.update(
            {interacao.exercicio.id: interacao
             for interacao in self})
        return sorted(exercicio2submissao.values(),
                      key=lambda i: i.exercicio.id)


InteracaoUsarioExercicioManager = InteracaoUsarioExercicioQuerySet.as_manager
