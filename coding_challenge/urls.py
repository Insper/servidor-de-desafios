from django.urls import path

from . import views


urlpatterns = [
    path('', views.CodingChallengeListView.as_view(), name='challenges'),
    path('<slug:slug>/', views.CodingChallengeView.as_view(), name='challenge'),
    path('<slug:slug>/submission', views.CodingChallengeSubmissionListView.as_view(), name='submissions'),
]
