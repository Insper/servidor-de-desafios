from django.urls import path

from . import views


urlpatterns = [
    path('admin/', views.list_quizzes, name='quizzes'),
    path('admin/<slug:slug>/', views.quiz_details, name='quiz-admin'),
    path('admin/<slug:slug>/userquiz/', views.list_user_quizzes, name='user-quizzes'),
    path('<slug:slug>/', views.QuizView.as_view(), name='quiz'),
    path('<slug:slug>/remaining-time/', views.get_remaining_time, name='quiz-remaining-time'),
]
