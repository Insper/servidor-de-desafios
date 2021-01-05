from django.urls import path

from . import views


urlpatterns = [
    path('', views.list_pages, name='pages_list'),
    path('<slug:concept_slug>/<slug:page_slug>/', views.get_page, name='page'),
]
