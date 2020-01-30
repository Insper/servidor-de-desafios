from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from enum import Enum
import markdown
from collections import namedtuple, defaultdict
from .models_helper import *
from .managers import ExercicioManager, RespostaExProgramacaoManager, ProvaManager, TurmaManager, ExercicioProgramadoManager, ViewDeExercicioManager
from .choices import Resultado


class Usuario(AbstractUser):
    def todas_turmas(self):
        return Turma.objects.do_aluno(self)

    def turmas_atuais(self):
        return Turma.objects.atuais().do_aluno(self)

    def exercicios_programados_disponiveis(self):
        return ExercicioProgramado.objects.disponiveis_para(self)

    def exercicios_disponiveis(self):
        return Exercicio.objects.disponiveis_para(self)


class Turma(models.Model):
    nome = models.CharField(max_length=1024, blank=True)
    inicio = models.DateField('data inicio', blank=True, null=True)
    fim = models.DateField('data fim', blank=True, null=True)

    objects = TurmaManager()

    class Meta:
        ordering = ['inicio']

    def __str__(self):
        return self.nome

    def esta_matriculado(self, aluno):
        try:
            Matricula.objects.get(aluno_id=aluno.id, turma_id=self.id)
            return True
        except Matricula.DoesNotExist:
            return False
        return False


class Matricula(models.Model):
    aluno = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    exercicios_liberados = models.BooleanField(default=False)

    class Meta:
        unique_together = ('aluno', 'turma')


class Tag(models.Model):
    nome = models.CharField(max_length=128)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Exercicio(models.Model):
    titulo = models.CharField(max_length=1024, blank=True)
    descricao = models.TextField(blank=True)
    imagem = models.ImageField(upload_to=DIR_EXERCICIOS, blank=True)
    publicado = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag)

    objects = ExercicioManager()

    @property
    def titulo_completo(self):
        titulo = '{0}'.format(self.id)
        if self.titulo:
            titulo += '. {0}'.format(self.titulo)
        return titulo

    @property
    def descricao_html(self):
        return markdown.markdown(self.descricao,
                                 extensions=['extra', 'codehilite'])

    def __str__(self):
        return self.titulo_completo

    def especifico(self):
        for modelo in ViewDeExercicio.objects.modelos():
            if hasattr(self, modelo):
                return getattr(self, modelo)
        return self


class ExercicioProgramado(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    exercicio = models.ForeignKey(Exercicio, on_delete=models.CASCADE)
    inicio = models.DateTimeField('data inicio', default=timezone.now)
    fim = models.DateTimeField('data fim', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'exercicios programados'

    objects = ExercicioProgramadoManager()


class ExercicioDeProgramacao(Exercicio):
    testes = models.FileField(upload_to=DIR_TESTES,
                              default=criar_arquivo_de_testes_padrao)
    nome_funcao = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name_plural = 'exercicios de programacao'


class RespostaSubmetida(models.Model):
    exercicio = models.ForeignKey(Exercicio, on_delete=models.CASCADE)
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data_submissao = models.DateTimeField('data submissao', auto_now_add=True)

    class Meta:
        abstract = True
        verbose_name_plural = 'respostas submetidas'


class RespostaExProgramacao(RespostaSubmetida):
    DetalhesDoErro = namedtuple('DetalhesDoErro', 'mensagem, stacktrace')

    feedback = models.TextField(blank=True)
    erros = models.TextField(blank=True)
    codigo = models.FileField(upload_to=caminho_submissoes_usuario)
    resultado = models.CharField(max_length=2,
                                 choices=Resultado.choices,
                                 blank=True)
    deletado = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'respostas exercicios de programacao'

    all_objects = RespostaExProgramacaoManager(incluir_deletados=True)
    objects = RespostaExProgramacaoManager()

    def __str__(self):
        return '{0}: Ex{1} - data[{2}] resultado[{3}]'.format(
            self.autor.username, self.exercicio.id, self.data_submissao,
            self.resultado)

    @property
    def sucesso(self):
        return self.resultado == Resultado.OK

    @property
    def lista_de_falhas(self):
        return self.feedback.split(FEEDBACK_SEP)

    @lista_de_falhas.setter
    def lista_de_falhas(self, feedbacks):
        feedback = FEEDBACK_SEP.join(feedbacks)
        if not feedback:
            feedback = 'Sem erros.'
        self.feedback = feedback

    @property
    def stack_traces(self):
        return self.erros.split(STACKTRACE_SEP)

    @stack_traces.setter
    def stack_traces(self, erros):
        erros = STACKTRACE_SEP.join(erros)
        if not erros:
            erros = '-'
        self.erros = erros

    @property
    def stack_traces_limpos(self):
        retval = []
        for st in self.stack_traces:
            limpo = st
            if 'AssertionError' in limpo:
                limpo = 'Resposta diferente da esperada.'
            else:
                inicio = limpo.rfind(STACKTRACE_FILE_PATTERN)
                if inicio >= 0:
                    limpo = limpo[inicio + len(STACKTRACE_FILE_PATTERN):]
            limpo = limpo.replace('<', '&lt;').replace('>', '&gt;').replace(
                '\n', '<br>').replace(' ', '&nbsp;')
            retval.append(limpo)
        return retval

    @property
    def feedback_limpo(self):
        msgs = self.lista_de_falhas
        stacktraces = ['' for _ in msgs]
        sts = self.stack_traces_limpos
        stacktraces[:len(sts)] = sts
        return list(
            set([
                RespostaExProgramacao.DetalhesDoErro(msg, st)
                for msg, st in zip(msgs, stacktraces)
            ]))


class Prova(models.Model):
    inicio = models.DateTimeField('data inicial')
    fim = models.DateTimeField('data final')
    titulo = models.CharField(max_length=1024, blank=True)
    descricao = models.TextField(blank=True)
    exercicios = models.ManyToManyField(ExercicioProgramado)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    slug = models.SlugField()

    objects = ProvaManager()

    def __str__(self):
        return self.titulo

    def disponivel_para(self, usuario):
        agora = timezone.now()
        horario_ok = self.inicio <= agora and agora <= self.fim
        return self.turma.esta_matriculado(usuario) and horario_ok

    @property
    def exercicios_por_nome(self):
        return self.exercicios.order_by('exercicio__titulo')


class ViewDeExercicio(models.Model):
    modelo = models.CharField(max_length=1024, blank=False, unique=True)
    view = models.CharField(max_length=1024, blank=False)

    objects = ViewDeExercicioManager()
