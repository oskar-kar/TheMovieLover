from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.Recommendations.as_view(), name='Recommend'),
]