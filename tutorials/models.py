from django.db import models
from core.models import Usuario, Exercicio
import markdown


class Tutorial(Exercicio):
    replit_url = models.CharField(max_length=1024, blank=True)

    class Meta:
        verbose_name_plural = 'tutoriais'

    @property
    def titulo_completo(self):
        return '[TUTORIAL] {0}'.format(self.titulo)

    @property
    def slides_html(self):
        substituicoes = [
            ('<span class="o">&amp;</span><span class="n">gt</span><span class="p">;</span>',
             '>'),
            ('<span class="o">&amp;</span><span class="n">lt</span><span class="p">;</span>',
             '<'),
        ]
        resultado = markdown.markdown(self.descricao,
                                      extensions=['codehilite'])
        slides = []
        for slide_str in resultado.split('---slide---')[1:]:
            com_div = '<div class="slide">\n'
            for linha in slide_str.split('\n'):
                for texto, substituicao in substituicoes:
                    linha = linha.replace(texto, substituicao)
                com_div += linha + '\n'
            com_div += '</div>\n'
            slides.append(com_div)
        return slides

    @property
    def todos_slides_html(self):
        return '\n'.join(self.slides_html)

    @property
    def total_slides(self):
        return self.descricao.count('---slide---')


class AcessoAoTutorial(models.Model):
    primeiro_acesso = models.DateTimeField('primeiro acesso',
                                           auto_now_add=True)
    ultimo_acesso = models.DateTimeField('ultimo acesso', auto_now=True)
    total_acessos = models.IntegerField(default=0)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'acessos ao tutorial'

    def __str__(self):
        return '{0}: Tutorial {1} Primeiro Acesso[{2}] Último Acesso[{3}] Total de Acessos[{4}]'.format(
            self.usuario.username, self.tutorial.id, self.primeiro_acesso,
            self.ultimo_acesso, self.total_acessos)
