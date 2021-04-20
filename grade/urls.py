from django.urls import path

from . import views


urlpatterns = [
    path('admin/', views.all_current_grades, name='all-current-grades'),
    path('', views.current_grades, name='current-grade'),
]
