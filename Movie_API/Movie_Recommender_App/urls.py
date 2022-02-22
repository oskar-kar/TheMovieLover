from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from django.views.generic import TemplateView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views

urlpatterns = [
    path('recommendations', views.AllMovies.as_view(), name='movies')
]
