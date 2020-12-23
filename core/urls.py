from core.views import change_password
from django.urls import include, path
from . import views


urlpatterns = [
    path('user/', views.get_user),
    path('change-password/', views.change_password),
    path('code/', include('code_challenge.urls')),
    path('trace/', include('trace_challenge.urls')),
]
