from django.urls import path

from . import views


urlpatterns = [
    path('', views.list_contents, name='contents_list'),
    path('page/', views.list_pages, name='pages_list'),
    path('page/<slug:content_slug>/', views.get_page, name='page'),
    path('page/<slug:content_slug>/<slug:page_slug>/', views.get_page, name='content_page'),
]
