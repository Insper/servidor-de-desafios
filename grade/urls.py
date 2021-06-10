from django.urls import path

from . import views


urlpatterns = [
    path('admin/', views.all_current_grades, name='all-current-grades'),
    path('admin/schema/', views.get_grade_schema, name='grades-schema'),
    path('admin/user/<str:username>/', views.get_user_grade, name='user-grades'),
    path('admin/user/<str:username>/<str:quiz_slug>/updated/', views.get_userquiz_updated, name='user-grade-updated'),
    path('admin/code/', views.all_current_code_grades, name='all-code-grades'),
    path('admin/code/<str:code_exercise_slug>/', views.get_code_grade, name='get-code-grade'),
    path('admin/code/<str:code_exercise_slug>/feedback/', views.get_code_feedbacks, name='all-code-grades'),
    path('admin/code/<str:code_exercise_slug>/ungraded/', views.get_ungraded_users, name='get-ungraded'),
    path('admin/code/<str:code_exercise_slug>/grade/<str:username>/', views.grade_code_exercise, name='grade-code-user'),
    path('', views.current_grades, name='current-grade'),
]
