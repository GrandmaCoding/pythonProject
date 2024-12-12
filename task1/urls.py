# from django.contrib import admin
from django.urls import path, include
from .views import home
from . import views

urlpatterns = [
    path('', home, name='home'),
    path('addpage', views.addpage, name='addpage'),
]
