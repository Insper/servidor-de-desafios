from django.urls import path

from . import views

urlpatterns = [
    path('', views.tutorials, name='tutorials'),
    path('<int:t_id>', views.tutorial, name='tutorial'),
]