from django.urls import include, path
from . import views


urlpatterns = [
    path('user/', views.get_user),
    path('coding/', include('coding_challenge.urls')),
]
