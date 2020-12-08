from django.urls import include, path


urlpatterns = [
    path('coding', include('coding_challenge.urls')),
]
