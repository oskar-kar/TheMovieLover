import time
import unittest
from datetime import datetime
from django.test import TestCase
from django.utils import timezone
from django.test import TestCase
from DBHandler import models
import random
from django.db import connection, transaction
from Movie_Recommender import wsgi
from django_pandas.io import read_frame
import warnings
warnings.filterwarnings("ignore")


class RecommenderTests(unittest.TestCase):
    def setUp(self):
        users = list(models.User.objects.all())
        self.users = random.sample(users, 20)

    def test_performance(self):
        for user in self.users:
            time1 = time.time()
            wsgi.RECOMMENDER.get_recommendations(user.id)
            time2 = time.time()
            time_delta = time2 - time1
            self.assertLess(time_delta, 1.0)

    def test_accuracy(self):
        cursor = connection.cursor()
        i = 0
        for user in self.users:
            rating = list(models.UsersRatings.objects.filter(userid=user.id).order_by('-datetime'))[-1]
            query = ''' INSERT INTO users_ratings (titleId,userId,rating,datetime) 
                        VALUES (%s,%s,%s,%s) '''
            values = (rating.titleid.titleid, rating.userid.id, rating.rating, rating.datetime)
            rating.delete()
            recommendations = wsgi.RECOMMENDER.get_recommendations(values[1])
            movies_in_rec = recommendations.filter(titleid=values[0])
            i += len(movies_in_rec)
            cursor.execute(query, values)
            transaction.commit()
        print('recommender acc: ', i/len(self.users))
        self.assertGreater(i/len(self.users), 0.6)

    def test_diversity(self):
        movies_dict = {}
        for user in self.users:
            movies = list(wsgi.RECOMMENDER.get_recommendations(user.id))
            for movie in movies:
                movies_dict[movie.titleid] = movies_dict.get(movie.titleid, 0) + 1
        unique_movies = len(movies_dict.values())
        mean_values = sum(movies_dict.values())/len(movies_dict.values())
        print('unique_movies: ', unique_movies, 'mean_values: ', mean_values)
        self.assertGreater(unique_movies, len(self.users)*8*0.6)







