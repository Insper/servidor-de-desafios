from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('evolution', views.evolution, name='evolution'),
    path('tutorials', views.tutorials, name='tutorials'),
    path('challenges', views.challenges, name='challenges'),
    path('download', views.download, name='download_report'),
    path('status', views.status, name='status'),
]
