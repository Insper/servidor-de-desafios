from django.urls import path

from . import views


urlpatterns = [
    path('', views.CodeChallengeListView.as_view(), name='challenges'),
    path('<slug:slug>/', views.CodeChallengeView.as_view(), name='challenge'),
    path('<slug:slug>/submission', views.CodeChallengeSubmissionListView.as_view(), name='submissions'),
    path('<slug:slug>/submission/<int:submission_id>/code', views.CodeChallengeSubmissionCodeView.as_view(), name='submission_code'),
]
