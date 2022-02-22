import os
import django
import pandas as pd
from DBHandler import models
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import connection, transaction

def populate_db():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.py')
    django.setup()

    scores = pd.read_csv(r'data\genome-scores.csv', low_memory=False)
    scores = scores[scores['relevance'] > 0.8]
    tags = pd.read_csv(r'data\genome-tags.csv', low_memory=False)
    links = pd.read_csv(r'data\links.csv', low_memory=False, dtype={'imdbId': str})
    links = links.drop(columns=['tmdbId'])
    df = scores.merge(tags, how='left', on='tagId')
    del scores
    df = df.merge(links, how='left', on='movieId')
    df['imdbId'] = "tt" + df['imdbId']
    movies = models.Movies.objects.all()
    i = 0
    movies_id = []
    print("Adding movies tags...")
    for movie in movies:
        temp_df = df[df['imdbId'] == movie.titleid].sort_values(by='relevance', ascending=False)
        str_tags = ','.join(s for s in temp_df['tag'].tolist())
        movie.tags = str_tags
        movie.save()
        movies_id.append(movie.titleid)
        i += 1
        if i % 100 == 0:
            print("Tags added to " + format((i / len(movies)) * 100, '.2f') + "% of movies")
    print("Added all movies tags")
    del df

    movies_id = pd.DataFrame(movies_id, columns=['imdbId'])
    ratings = pd.read_csv(r'data\ratings.csv')
    ratings = ratings[ratings['timestamp'] > 1483225201]
    ratings_per_user = ratings.groupby('userId').count()['rating'] > 20
    ratings_per_user = pd.DataFrame(ratings_per_user.reset_index())
    ratings_per_user = ratings_per_user[ratings_per_user['rating']]
    ratings = ratings[ratings['userId'].isin(ratings_per_user['userId'].to_list())]

    ratings = ratings.merge(links, how='left', on='movieId')

    ratings['datetime'] = ratings['timestamp'].apply(lambda x: datetime.fromtimestamp(x, tz=timezone.utc))
    ratings = ratings.drop(columns=['timestamp'])
    ratings['imdbId'] = "tt" + ratings['imdbId']
    ratings = ratings[~ratings['imdbId'].isin(movies)]
    ratings = movies_id.merge(ratings, how="left", on='imdbId')
    ratings = ratings.dropna(subset=['userId', 'movieId'])
    users = ratings['userId'].unique()
    print("Adding users")

    cursor = connection.cursor()
    cursor.execute("SET IDENTITY_INSERT dbo.auth_user ON")
    query = ''' INSERT INTO auth_user 
            (id,username,email,password, date_joined,is_superuser,first_name, last_name,is_staff,is_active) 
            VALUES (%s,%s,%s,%s,%s,0,'a','a' ,0,0) '''
    query_list = ((userid, "populatedb" + str(userid), "populatedb@fakeemail.com",
                   "hardcoded_password", datetime.now(tz=timezone.utc)) for userid in users)
    cursor.executemany(query, query_list)
    transaction.commit()
    ratings['rating'] = ratings['rating'] * 2
    print("Users added\nAdding movies ratings...")

    query = ''' INSERT INTO users_ratings
                (titleId,userId,rating,datetime) 
                VALUES (%s,%s,%s,%s) '''
    ratings = ratings.drop(columns=['movieId'])
    query_list = tuple(ratings.itertuples(index=False, name=None))

    cursor.executemany(query, query_list)
    transaction.commit()
    print("Added all movies ratings")
