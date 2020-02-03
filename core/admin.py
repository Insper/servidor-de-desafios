from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms import CheckboxSelectMultiple, ModelForm, FileField
from django.utils import timezone
from django.contrib.admin.filters import RelatedFieldListFilter
from io import TextIOWrapper
import pandas as pd
import random
import json

from .models import Usuario, Turma, Tag, Matricula, Exercicio, ExercicioProgramado, ExercicioDeProgramacao, RespostaSubmetida, RespostaExProgramacao, Prova, InteracaoUsarioExercicio
from .utils import CORES_ESCURAS_CSS


class MatriculaInline(admin.TabularInline):
    model = Matricula
    extra = 1
    classes = ['collapse']


class TagInline(admin.TabularInline):
    model = Exercicio.tags.through
    extra = 1


class CustomUserAdmin(UserAdmin):
    inlines = UserAdmin.inlines + [
        MatriculaInline,
    ]


class ExercicioAdmin(admin.ModelAdmin):
    inlines = (TagInline, )
    exclude = ('tags', )


class FilterComboBox(RelatedFieldListFilter):
    template = 'filter_template.html'


class RespostaExProgramacaoAdmin(admin.ModelAdmin):
    list_filter = [('autor', FilterComboBox), ('exercicio', FilterComboBox)]
    list_display = ('autor', 'exercicio', 'codigo', 'data_submissao',
                    'resultado')

    def soft_delete(self, request, queryset):
        queryset.update(deletado=True)

    soft_delete.short_description = 'Soft delete selecionados'

    actions = ['soft_delete']


class BlocoDeExercicios:
    def __init__(self, inicio, fim, exercicios=None):
        if not exercicios:
            exercicios = []

        self.inicio = inicio
        self.fim = fim
        self.exercicios = exercicios


def monta_blocos(exercicios_programados):
    blocos = {}
    for ex in exercicios_programados:
        inicio = ex.inicio
        fim = ex.fim
        bloco = blocos.setdefault((inicio, fim),
                                  BlocoDeExercicios(inicio, fim))
        bloco.exercicios.append(ex.exercicio)
    for bloco in blocos.values():
        bloco.exercicios.sort(key=lambda ex: ex.id)
    return list(blocos.values())


def _cria_contexto(contexto, turma_id=None):
    contexto = contexto or {}
    exercicios = Exercicio.objects.publicados()
    em_nenhum_bloco = exercicios
    try:
        turma = Turma.objects.get(pk=turma_id)
        exercicios_programados = turma.exercicioprogramado_set.all()
        blocos = monta_blocos(exercicios_programados)
        em_algum_bloco = set([e.exercicio for e in exercicios_programados])
        em_nenhum_bloco = set(exercicios) - em_algum_bloco
        contexto['blocos'] = blocos
    except Turma.DoesNotExist:
        pass
    contexto['em_nenhum_bloco'] = sorted(em_nenhum_bloco, key=lambda ex: ex.id)
    contexto['exercicios'] = exercicios
    contexto['todas_tags'] = Tag.objects.all()
    contexto['tag_classes'] = {
        tag.nome: random.choice(CORES_ESCURAS_CSS)
        for tag in Tag.objects.all()
    }
    return contexto


class TurmaForm(ModelForm):
    arquivo_alunos = FileField()

    class Meta:
        model = Turma
        fields = '__all__'


class TurmaAdmin(admin.ModelAdmin):
    change_form_template = 'admin/core/turma_change_form.html'
    inlines = (MatriculaInline, )
    fieldsets = ((None, {
        'fields': (
            'nome',
            'inicio',
            'fim',
        )
    }), ('Arquivo de alunos (Blackboard)', {
        'fields': ('arquivo_alunos', )
    }))

    form = TurmaForm

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = _cria_contexto(extra_context)
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = _cria_contexto(extra_context, object_id)
        return super().change_view(request, object_id, form_url, extra_context)

    def adiciona_alunos(self, arquivo, obj):
        text_f = TextIOWrapper(arquivo, encoding='utf-16')
        df = pd.read_csv(text_f, sep='\t')

        for user_data in df.iterrows():
            primeiro_nome = user_data[1]['Nome']
            try:
                sobrenome = user_data[1]['Sobrenome']
            except:
                primeiro_nome = primeiro_nome.split(' ')[0]
                sobrenome = ' '.join(primeiro_nome.split(' ')[1:])
            username = user_data[1]['Nome do usuário']
            email = username + '@al.insper.edu.br'
            usuarios_com_mesmo_nome = Usuario.objects.filter(username=username)
            if not usuarios_com_mesmo_nome:
                print('Criando usuário: {0}'.format(username))
                Usuario.objects.create_user(username=username,
                                            email=email,
                                            password=username,
                                            first_name=primeiro_nome,
                                            last_name=sobrenome)
            usuario = Usuario.objects.get(username=username)
            alunos_matriculados = obj.alunos()
            if usuario not in alunos_matriculados:
                print('Adicionando {0} em {1}'.format(usuario, obj))
                obj.matricula(usuario)
        obj.save()

    def save_model(self, request, obj, form, change):
        self.adiciona_alunos(form.cleaned_data.get('arquivo_alunos'), obj)
        super().save_model(request, obj, form, change)
        exercicios = {e.id: e for e in Exercicio.objects.publicados()}
        # Sempre deletar todos os exercícios programados anteriores (dessa turma),
        # pois não queremos guardar o histórico (é só lixo)
        ExercicioProgramado.objects.filter(turma__id=obj.id).delete()
        blocos = json.loads(request.POST['blocos'])
        date_fmt = '%d/%m/%Y'
        for bloco in blocos:
            inicio = bloco['inicio']
            if inicio:
                inicio = timezone.datetime.strptime(inicio, date_fmt)
            else:
                inicio = None
            fim = bloco['fim']
            if fim:
                fim = timezone.datetime.strptime(fim, date_fmt)
            else:
                fim = None
            for e_id in bloco['exercicios']:
                exercicio = ExercicioProgramado(turma=obj,
                                                exercicio=exercicios[e_id],
                                                inicio=inicio,
                                                fim=fim)
                exercicio.save()


# Registra páginas de admin
admin.site.register(Usuario, CustomUserAdmin)
admin.site.register(Turma, TurmaAdmin)
admin.site.register(Matricula)
admin.site.register(Tag)
admin.site.register(ExercicioProgramado)
admin.site.register(ExercicioDeProgramacao, ExercicioAdmin)
admin.site.register(RespostaExProgramacao, RespostaExProgramacaoAdmin)
admin.site.register(InteracaoUsarioExercicio)
admin.site.register(Prova)
