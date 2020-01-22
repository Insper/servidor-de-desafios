from django.urls import path

from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.index, name='index'),
    path('challenge', views.index, name='index'),
    path('challenge/<int:c_id>', views.challenge, name='challenge'),
    path('teste-de-mesa/<int:pk>', views.teste_de_mesa, name='teste_de_mesa'),
    path('prova', views.ProvasListView.as_view(), name='provas'),
    path('prova/<slug:slug>', views.ProvaDetailView.as_view(), name='prova'),
    path('sandbox', views.sandbox, name='sandbox'),
    path('agradecimentos', TemplateView.as_view(template_name='challenges/thanks.html'), name='agradecimentos'),
]
