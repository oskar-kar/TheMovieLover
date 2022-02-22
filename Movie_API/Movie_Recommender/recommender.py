from collections import defaultdict
import time

import pandas as pd
from DBHandler import models
import numpy as np
from Movie_Recommender_App import views
from django_pandas.io import read_frame
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from itertools import islice


class Recommender:
    def __init__(self):
        self.content_indexes = []
        self.collaborative_indexes = []
        self.tags = []
        self.content_recommender, self.collaborative_recommender = self.init_recommenders()

    def init_recommenders(self):
        time1 = time.time()
        print("Initializing recommender....")
        movies = models.Movies.objects.all()
        movies = read_frame(movies, fieldnames=['titleid', 'tags', 'avgratingimdb'])
        movies['avgratingimdb'] = pd.to_numeric(movies['avgratingimdb'])
        ratings = models.UsersRatings.objects.all()
        ratings = read_frame(ratings, verbose=False, fieldnames=['titleid', 'rating', 'userid'])

        movies_merged_df = movies.merge(ratings, on='titleid', how='left').fillna(0)
        movie_features_df = movies_merged_df.pivot(index='userid', columns='titleid', values='rating').fillna(0)
        self.collaborative_indexes = movies_merged_df.index.array
        movie_features_df_matrix = csr_matrix(movie_features_df.values)
        collaborative_model = NearestNeighbors(metric='cosine', algorithm='brute')
        collaborative_model.fit(movie_features_df_matrix)

        movie_tag_df = pd.DataFrame(columns=['titleid', 'tag', 'rating'])
        for index, row in movies.iterrows():
            df = pd.DataFrame(row['tags'].split(","), columns=['tag'])
            df['titleid'] = row['titleid']
            df['rating'] = row['avgratingimdb']
            movie_tag_df = movie_tag_df.append(df, ignore_index=True)

        movie_tag_pivot = movie_tag_df.pivot(index='titleid', columns='tag', values='rating').fillna(0)
        self.tags = movie_tag_pivot.columns.array
        self.content_indexes = movie_tag_pivot.index.array
        movie_tags_df_matrix = csr_matrix(movie_tag_pivot.values)
        content_model = NearestNeighbors(metric='cosine', algorithm='brute')
        content_model.fit(movie_tags_df_matrix)
        time2 = time.time()
        print('function took {:.3f} ms'.format((time2-time1)*1000.0))
        print("Recommender initialized")

        return content_model, collaborative_model

    def get_recommendations(self, userid):
        user_ratings = models.UsersRatings.objects.filter(userid=userid)
        user_ratings = read_frame(user_ratings, verbose=False, fieldnames=['titleid', 'rating', 'userid'])
        movies = models.Movies.objects.all()
        movies = read_frame(movies, fieldnames=['titleid', 'tags'])

        rec1 = self._get_content_recommendations(userid, user_ratings, movies)
        rec2 = self._get_collaborative_recommendations(userid, user_ratings, movies)

        recommendations = [rec for rec in rec1 if rec in rec2]
        i = 0
        while len(recommendations) < 8:
            if rec1[i] not in recommendations:
                recommendations.append(rec1[i])
            if rec2[i] not in recommendations:
                recommendations.append(rec2[i])
            i += 1
        recommended_movies = models.Movies.objects.filter(titleid__in=recommendations[:8])
        return recommended_movies

    def _get_content_recommendations(self, userid, user_ratings, movies):
        mean_rating = user_ratings['rating'].mean()
        user_watched_titles = user_ratings['titleid'].tolist()
        user_ratings = user_ratings[user_ratings['rating'] >= mean_rating]
        user_ratings = user_ratings.merge(movies, how='left', on='titleid')

        rating_tags = []
        for index, row in user_ratings.iterrows():
            tmp_tags = row['tags'].split(",")
            for tag in tmp_tags:
                rating_tags.append([tag, row['rating'], row['titleid']])
        movie_tag_df = pd.DataFrame(rating_tags, columns=['tags', 'rating', 'titleid'])
        movie_tag_pivot = movie_tag_df.pivot(index='titleid', columns='tags', values='rating').fillna(0)

        missing_tags = [tag for tag in self.tags if tag not in movie_tag_pivot.columns.array]
        movie_tag_pivot[missing_tags] = 0
        movie_tag_pivot = movie_tag_pivot[self.tags]

        distances, indices = self.content_recommender.kneighbors(
            movie_tag_pivot.values, n_neighbors=10)

        recommended_films = np.unique(indices.flatten())
        recommended_films = (self.content_indexes[film_index] for film_index in
                             recommended_films if self.content_indexes[film_index] not in user_watched_titles)
        recommended_films = list(islice(recommended_films, 20))
        return recommended_films

    def _get_collaborative_recommendations(self, userid, user_ratings, movies):
        movies = pd.DataFrame(movies['titleid'])
        movies_merged_df = movies.merge(user_ratings, how='left', on='titleid')
        movies_merged_df['userid'] = movies_merged_df['userid'].fillna(userid)
        movies_merged_df.fillna(0, inplace=True)

        movie_features_df = movies_merged_df.pivot(index='userid', columns='titleid', values='rating').fillna(0)
        distances, indices = self.collaborative_recommender.kneighbors(
            movie_features_df.iloc[0].values.reshape(1, -1), n_neighbors=15)

        user_watched_titles = user_ratings['titleid'].tolist()
        similar_users = indices.flatten().tolist()
        similar_users = [self.collaborative_indexes[user_index] for user_index in similar_users]
        similar_users_ratings = models.UsersRatings.objects.filter(
            userid__in=similar_users)
        similar_users_ratings = read_frame(
            similar_users_ratings, verbose=False, fieldnames=['titleid', 'rating', 'userid'])
        similar_users_ratings = similar_users_ratings[~similar_users_ratings['titleid'].isin(user_watched_titles)]
        recommended_films = similar_users_ratings.groupby('titleid').sum()
        recommended_films.sort_values(by=['rating'], inplace=True, ascending=False)
        return recommended_films.index.array[:20]

