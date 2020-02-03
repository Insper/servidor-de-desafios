from django.urls import path

from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.index, name='index'),
    path('exercicio', views.index, name='index'),
    path('exercicio/<int:c_id>', views.exercicio, name='exercicio'),
    path('prova', views.ProvasListView.as_view(), name='provas'),
    path('prova/<slug:slug>', views.ProvaDetailView.as_view(), name='prova'),
    path('sandbox', views.sandbox, name='sandbox'),
    path('agradecimentos',
         TemplateView.as_view(template_name='core/thanks.html'),
         name='agradecimentos'),
]
