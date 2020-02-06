from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cmd1/', views.cmd1),
    path('cmd3/', views.cmd3)
]