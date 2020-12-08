from django.urls import path

from . import views


urlpatterns = [
    path('', views.CodingChallengeList.as_view(), name='index'),
]
