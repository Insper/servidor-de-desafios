from django.urls import path

from . import views


urlpatterns = [
    path('', views.TraceChallengeListView.as_view(), name='trace_challenges'),
    path('interaction/', views.TraceInteractionListView.as_view(), name='trace_interaction_list'),
    path('<slug:slug>/', views.TraceChallengeView.as_view(), name='trace_challenge'),
    path('<slug:slug>/memory/<int:state_index>', views.get_memory, name='trace_memory'),
    path('<slug:slug>/state/', views.TraceStateListView.as_view(), name='trace_state_list'),
]
