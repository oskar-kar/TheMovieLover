from django.urls import path, include
from . import views

urlpatterns = [
    path('users/', include('UsersHandler.urls')),
    path('movies', views.AllMovies.as_view(), name='movies'),
    path('movies/info', views.MoviesAllInfo.as_view(), name='movies'),
    path('movies/recommend', include('RecommendationHandler.urls')),
    path('actors', views.Actors.as_view(), name='actors'),
    path('directors', views.Directors.as_view(), name='directors'),
    path('writers', views.Writers.as_view(), name='writers'),
    path('rating', views.Ratings.as_view(), name='ratings')
]