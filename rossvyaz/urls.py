from django.urls import path

from . import views

app_name = 'rossvyaz'
urlpatterns = [
    path('search', views.search_view, name='search'),
    path('api/search', views.SearchAPI.as_view(), name='search_api'),
]