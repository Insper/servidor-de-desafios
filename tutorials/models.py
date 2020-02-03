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
    def descricao_html(self):
        substituicoes = [
            ('<span class="o">&amp;</span><span class="n">gt</span><span class="p">;</span>',
             '>'),
            ('<span class="o">&amp;</span><span class="n">lt</span><span class="p">;</span>',
             '<'),
        ]
        resultado = markdown.markdown(self.descricao,
                                      extensions=['codehilite'])
        com_div = ''
        slide_id = 1
        for linha in resultado.split('\n'):
            if '---slide---' in linha:
                if slide_id > 1:
                    com_div += '</div>\n'
                com_div += '<div class="slide" id="slide{0}">\n'.format(
                    slide_id)
                slide_id += 1
            else:
                for texto, substituicao in substituicoes:
                    linha = linha.replace(texto, substituicao)
                com_div += linha + '\n'
        if slide_id > 1:
            com_div += '</div>\n'
        return com_div


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
