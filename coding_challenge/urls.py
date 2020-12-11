from django.urls import path

from . import views


urlpatterns = [
    path('', views.CodingChallengeListView.as_view(), name='index'),
    path('<slug:slug>/', views.CodingChallengeView.as_view(), name='detail'),
]
