from django.urls import path

from . import views


urlpatterns = [
    path('admin/', views.all_current_grades, name='all-current-grades'),
    path('admin/schema/', views.get_grade_schema, name='grades-schema'),
    path('admin/user/<str:username>/', views.get_user_grade, name='user-grades'),
    path('', views.current_grades, name='current-grade'),
]
