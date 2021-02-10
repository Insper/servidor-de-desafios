from django.urls import path

from . import views


urlpatterns = [
    path('<slug:slug>/', views.QuizView.as_view(), name='quiz'),
    path('<slug:slug>/remaining-time/', views.get_remaining_time, name='quiz-remaining-time'),
]
