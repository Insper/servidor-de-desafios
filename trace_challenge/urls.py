from django.urls import path

from . import views


urlpatterns = [
    path('', views.TraceChallengeListView.as_view(), name='trace_challenges'),
    path('<slug:slug>/', views.TraceChallengeView.as_view(), name='trace_challenge'),
    path('<slug:slug>/state/', views.TraceStateListView.as_view(), name='trace_state_list'),
    # path('<slug:slug>/submission', views.CodeChallengeSubmissionListView.as_view(), name='submissions'),
    # path('<slug:slug>/submission/<int:submission_id>/code', views.CodeChallengeSubmissionCodeView.as_view(), name='submission_code'),
]
