from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('total-por-aluno', views.total_por_aluno, name='total_por_aluno'),
    path('evolucao', views.evolucao, name='evolucao'),
    path('tutoriais', views.tutoriais, name='tutoriais'),
    path('exercicios-de-programacao',
         views.exercicios_de_programacao,
         name='exercicios-de-programacao'),
    path('download', views.download, name='download_relatorio'),
    path('situacao', views.situacao, name='situacao'),
]
