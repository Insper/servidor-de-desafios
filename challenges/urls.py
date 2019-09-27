from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('challenge', views.index, name='index'),
    path('challenge/<int:c_id>', views.challenge, name='challenge'),
    path('prova', views.ProvasListView.as_view(), name='provas'),
    path('prova/<slug:slug>', views.ProvaDetailView.as_view(), name='prova'),
    path('sandbox', views.sandbox, name='sandbox'),
]