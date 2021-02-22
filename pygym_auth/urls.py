from django.urls import path
from rest_framework.authtoken import views as authviews
from . import views


urlpatterns = [
    path('token/', authviews.obtain_auth_token),
    path('change-password/', views.change_password),
    path('signup/', views.signup),
    path('confirm/', views.email_confirmation),
]
