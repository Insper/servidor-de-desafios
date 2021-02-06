from core.views import change_password
from django.urls import include, path
from rest_framework.authtoken import views as authviews
from . import views


urlpatterns = [
    path('token/', authviews.obtain_auth_token),
    path('user/', views.get_user),
    path('change-password/', views.change_password),
    path('concept/', views.ConceptListView.as_view()),
    path('concept/<slug:slug>/', views.get_concept),
    path('code/', include('code_challenge.urls')),
    path('trace/', include('trace_challenge.urls')),
    path('content/', include('content.urls')),
    path('thanks/', include('thanks.urls')),
]
