
from django.core import serializers as sr
from rest_framework.generics import GenericAPIView

from rest_framework.response import Response
from rest_framework import status
from Movie_Recommender import wsgi
import time
from DBHandler import models
from datetime import timedelta
from django.utils import timezone
from django_pandas.io import read_frame

class AllMovies(GenericAPIView):

    def get(self, request, format='json'):
        time1 = time.time()
        if "userId" in request.query_params:
            try:
                user_id = request.query_params["userId"]
                movies = wsgi.RECOMMENDER.get_recommendations(user_id)
            except Exception as e:
                date_week_ago = timezone.now().date() - timedelta(days=7)
                user_ratings = models.UsersRatings.objects.filter(datetime__gte=date_week_ago)
                user_ratings = user_ratings = read_frame(user_ratings, verbose=False,
                                                         fieldnames=['titleid', 'rating', 'userid'])
                recommended_films = user_ratings.groupby('titleid').sum()
                recommended_films.sort_values(by=['rating'], inplace=True, ascending=False)
                movies = models.Movies.objects.filter(titleid__in=recommended_films.index.array[:8])
        else:
            try:
                date_week_ago = timezone.now().date() - timedelta(days=7)
                user_ratings = models.UsersRatings.objects.filter(datetime__gte=date_week_ago)
                user_ratings = user_ratings = read_frame(user_ratings, verbose=False,
                                                         fieldnames=['titleid', 'rating', 'userid'])
                recommended_films = user_ratings.groupby('titleid').sum()
                recommended_films.sort_values(by=['rating'], inplace=True, ascending=False)
                movies = models.Movies.objects.filter(titleid__in=recommended_films.index.array[:8])
            except Exception as e:
                movies = models.Movies.objects.all().order_by('-avgratingimdb')[:8]
        json = sr.serialize('json', movies)
        time2 = time.time()
        print('function took {:.3f} ms'.format((time2-time1)*1000.0))
        return Response(json, status=status.HTTP_200_OK)
