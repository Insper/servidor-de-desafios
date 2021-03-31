from django.urls import include, path
from . import views


urlpatterns = [
    path('auth/', include('pygym_auth.urls')),
    path('user/', views.get_user),
    path('user/admin/', views.list_users),
    path('user/admin/tag/', views.list_user_tags),
    path('concept/', views.ConceptListView.as_view()),
    path('concept/<slug:slug>/', views.get_concept),
    path('code/', include('code_challenge.urls')),
    path('trace/', include('trace_challenge.urls')),
    path('quiz/', include('quiz.urls')),
    path('content/', include('content.urls')),
    path('thanks/', include('thanks.urls')),
]
