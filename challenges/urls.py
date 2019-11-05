from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('challenge', views.index, name='index'),
    path('challenge/<int:c_id>/<str:word>', views.challenge, name='challenge'),
    path('sandbox', views.sandbox, name='sandbox'),
]