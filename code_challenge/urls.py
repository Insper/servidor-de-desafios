from django.urls import path

from . import views


urlpatterns = [
    path('', views.CodeChallengeListView.as_view(), name='challenges'),
    path('interaction/', views.CodeInteractionListView.as_view(), name='code_interaction_list'),
    path('admin/interaction/', views.list_interactions_for, name='list_interactions_for'),
    path('<slug:slug>/', views.CodeChallengeView.as_view(), name='challenge'),
    path('<slug:slug>/test-code/', views.get_test_code, name='challenge_test_code'),
    path('<slug:slug>/submission/', views.CodeChallengeSubmissionListView.as_view(), name='submissions'),
    path('<slug:slug>/submission/<int:submission_id>/code/', views.CodeChallengeSubmissionCodeView.as_view(), name='submission_code'),
]
