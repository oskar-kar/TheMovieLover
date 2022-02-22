
import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core import serializers as sr
from django.db import connection
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
import requests

from . import serializers
from . import models

UserModel = get_user_model()
# Create your views here.



# ---------/MoviesHandling/------------#
class MoviesAllInfo(GenericAPIView):

    title_param = openapi.Parameter('titleId', openapi.IN_QUERY, description="(required) searches for a movie with given id", type=openapi.TYPE_STRING)
    get_200_response = openapi.Response('Getting movie info from database was successful', serializers.MoviesSerializer)
    get_400_response = openapi.Response('Wrong or no parameters were given',serializers.RatingsSerializer)

    @swagger_auto_schema(manual_parameters=[title_param], responses={200: get_200_response})
    def get(self,request):

        if request.query_params:
            if 'titleId' in request.query_params:
                param = request.query_params['titleId']
                with connection.cursor() as cursor:
                    cursor.execute("""Select Q.*, STUFF(
						(SELECT ',' + primaryName
						 From names,movies_actors as ma
						 where ma.nconst = names.nconst and ma.tconst = Q.titleId
						 for xml path ('')),1,1,'') as Actors,
				STUFF(
						(SELECT ',' + primaryName
						 From names,movies_directors as md
						 where md.nconst = names.nconst and md.tconst = Q.titleId 
						 for xml path ('')),1,1,'') as Directors,
				STUFF(  
				        (SELECT ',' + primaryName
						 From names,movies_writers as mw
						 where mw.nconst = names.nconst and mw.tconst = Q.titleId 
						 for xml path ('')),1,1,'') as Writers
            from (select * from movies
		          where titleId = %s) as Q
            group by titleId, originalTitle, polishTitle, genres, year, avgRatingImdb, numVotesImdb, socialGroupLink,
            sourceLink, isNetflix, isAmazonPrime, isHBO, tags""", [param])

                    json = dictfetchall(cursor)
                    if json:
                        return Response(json,status= status.HTTP_200_OK)
            return Response(status= status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

class AllMovies(GenericAPIView):
    serializer_class = serializers.MoviesSerializer

    name_param = openapi.Parameter('username', openapi.IN_QUERY, description="(optional) searches for movies rated by this user with ratings in a column userratings_rating",
                                   type=openapi.TYPE_STRING)
    genres_param = openapi.Parameter('genres', openapi.IN_QUERY, description="(optional) multiple genres have to be sorted alphabetically and separated by a coma",
                                     type=openapi.TYPE_STRING)
    title_param = openapi.Parameter('originaltitle', openapi.IN_QUERY, description="(optional) searches for movies with given string in the orignal or polish title",
                                    type=openapi.TYPE_STRING)
    rating_param = openapi.Parameter('avgratingimdb', openapi.IN_QUERY, description="(optional) when 'True' sorts movies by rating in descending order, otherwise number sorts in ascending order",
                                     type=openapi.TYPE_BOOLEAN)
    votes_param = openapi.Parameter('numvotesimdb', openapi.IN_QUERY,
                                    description="(optional) when 'True' sorts movies by number of votes in descending order, otherwise sorts in ascending order",
                                    type=openapi.TYPE_BOOLEAN)
    min_param = openapi.Parameter('minindex', openapi.IN_QUERY,
                                  description="(optional) defines how many movies should be ignored in the beginning of the list",
                                  type=openapi.TYPE_INTEGER)
    max_param = openapi.Parameter('maxindex', openapi.IN_QUERY,
                                  description="(optional) defines how many movies should be sent",
                                  type=openapi.TYPE_INTEGER)
    get_200_response = openapi.Response('Getting movie info from database was successful', serializers.MoviesSerializer)

    @swagger_auto_schema(manual_parameters=[name_param, genres_param, title_param, rating_param, votes_param, min_param, max_param],
                         responses={200: get_200_response})
    def get(self, request, format='json'):

        movies = models.Movies.objects.all()

        if request.query_params: # Checks if any movie fields where specified

            if 'genres' in request.query_params:
                movies = movies.filter(genres__contains=request.query_params['genres'])

            if 'originaltitle' in request.query_params:
                movies = movies.filter(originaltitle__contains=request.query_params['originaltitle'])
                movies2 = models.Movies.objects.filter(polishtitle__contains=request.query_params['originaltitle'])
                movies = movies | movies2
            if 'avgratingimdb' in request.query_params:
                if request.query_params['avgratingimdb'].lower() == "true":
                    movies = movies.order_by('-avgratingimdb')
                elif request.query_params['avgratingimdb'].lower() == "false":
                    movies = movies.order_by('avgratingimdb')

            if 'numvotesimdb' in request.query_params:
                if request.query_params['numvotesimdb'].lower() == "true":
                    movies = movies.order_by('-numvotesimdb')
                elif request.query_params['numvotesimdb'].lower() == "false":
                    movies = movies.order_by('numvotesimdb')

            if "minindex" in request.query_params:
                if request.query_params['minindex'].isnumeric():
                    mini = int(request.query_params['minindex'])
                    movies = movies[mini:]
                else:
                    return Response(status= status.HTTP_400_BAD_REQUEST)

            if "maxindex" in request.query_params:
                sr.serialize('json', movies)
                if request.query_params['maxindex'].isnumeric():
                    maxi = int(request.query_params['maxindex'])
                    movies = movies[:maxi]
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

            if 'username' in  request.query_params:
                user = UserModel.objects.filter(username=request.query_params['username'])[0].id
                movies = movies.filter(usersratings__userid=user).values('titleid', 'originaltitle', 'polishtitle', 'genres', 'year',
                                                                         'avgratingimdb', 'numvotesimdb', 'socialgrouplink', 'sourcelink',
                                                                         'isnetflix', 'isamazonprime', 'ishbo','usersratings__rating')
                return Response(movies, status=status.HTTP_200_OK)
            json = sr.serialize('json', movies)
            return Response(json, status=status.HTTP_200_OK)  # Returns filtered list of movies from DB


        # When no movie fields where specified returns all movies from DB
        movies = models.Movies.objects.all()
        json = sr.serialize('json', movies)
        return Response(json, status=status.HTTP_200_OK)

    def post(self, request, format='json'):
        serializer = serializers.MoviesSerializer(data=request.data)
        if serializer.is_valid():
            lastmovie = models.Movies.objects.latest('titleid')
            id = int(lastmovie.titleid[2:])
            id = "tt" + str(id + 1)
            print(id)
            serializer.validated_data['titleid'] = id
            movie = serializer.save()
            if movie:
                json = sr.serialize('json', serializer)
                return Response(json, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Actors(GenericAPIView):
    serializer_class = serializers.PeopleSerializer

    def get(self, request, format='json'):


        serializer = serializers.ActorSerializer(data=request.query_params)

        if serializer.is_valid():
            if serializer.validated_data['tconst'] != '':
                movieid = models.Movies.objects.filter(titleid=serializer.data['tconst'])
                actor = models.Names.objects.filter(moviesactors__tconst=movieid[0])
            if serializer.validated_data['nconst'] != '':
                nameid = models.Movies.objects.filter(titleid=serializer.data['nconst'])
                actor = models.Names.objects.filter(nconst=nameid)
            json = sr.serialize('json', actor)
            return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format='json'):
        """
        tconst -- movie id
        nconst -- name id (should be blank)
        fullname -- name
        """
        print(request.data)
        titleid = request.data['tconst']
        name = request.data['fullname']
        lastname = models.Names.objects.latest('nconst')
        id = int(lastname.nconst[2:])
        id = "nm" + str(id + 1)
        namedata = {'nconst': id, 'primaryname': name}
        nameserializer = serializers.NameSerializer(data=namedata)
        if nameserializer.is_valid():
            done1 = nameserializer.save()
        else:
            return Response(nameserializer.errors, status=status.HTTP_400_BAD_REQUEST)
        actordata = {'tconst': titleid, 'nconst': id}
        actorserializer = serializers.ActorSerializer(data=actordata)
        if actorserializer.is_valid():
            actorserializer.validated_data['tconst'] = models.Movies.objects.filter(titleid=titleid)[0]
            actorserializer.validated_data['nconst'] = models.Names.objects.filter(nconst=id)[0]
            done2 = actorserializer.save()
        else:
            return Response(actorserializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if done2 and done1:
            data = {'tconst': titleid, 'nconst': id, 'fullname': name}
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)


class Directors(GenericAPIView):
    serializer_class = serializers.PeopleSerializer

    def get(self, request):
        serializer = serializers.DirectorSerializer(data=request.query_params)
        if serializer.is_valid():
            if serializer.validated_data['tconst'] != '':
                movieid = models.Movies.objects.filter(titleid=serializer.data['tconst'])
                director = models.Names.objects.filter(moviesdirectors__tconst=movieid[0])
            if serializer.validated_data['nconst'] != '':
                nameid = models.Movies.objects.filter(titleid=serializer.data['nconst'])
                director = models.Names.objects.filter(nconst=nameid)
            json = sr.serialize('json', director)
            return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format='json'):
        """
        tconst -- movie id
        nconst -- name id (should be blank)
        fullname -- name
        """
        print(request.data)
        titleid = request.data['tconst']
        name = request.data['fullname']
        lastname = models.Names.objects.latest('nconst')
        id = int(lastname.nconst[2:])
        id = "nm" + str(id + 1)
        namedata = {'nconst': id, 'primaryname': name}
        nameserializer = serializers.NameSerializer(data=namedata)
        if nameserializer.is_valid():
            done1 = nameserializer.save()
        else:
            return Response(nameserializer.errors, status=status.HTTP_400_BAD_REQUEST)
        directordata = {'tconst': titleid, 'nconst': id}
        directorserializer = serializers.DirectorSerializer(data=directordata)
        if directorserializer.is_valid():
            directorserializer.validated_data['tconst'] = models.Movies.objects.filter(titleid=titleid)[0]
            directorserializer.validated_data['nconst'] = models.Names.objects.filter(nconst=id)[0]
            done2 = directorserializer.save()
        else:
            return Response(directorserializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if done2 and done1:
            data = {'tconst': titleid, 'nconst': id, 'fullname': name}
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)


class Writers(GenericAPIView):
    serializer_class = serializers.PeopleSerializer

    def get(self, request):
        serializer = serializers.WriterSerializer(data=request.query_params)
        if serializer.is_valid():
            if serializer.validated_data['tconst'] != '':
                movieid = models.Movies.objects.filter(titleid=serializer.data['tconst'])
                writer = models.Names.objects.filter(movieswriters__tconst=movieid[0])
            if serializer.validated_data['nconst'] != '':
                nameid = models.Movies.objects.filter(titleid=serializer.data['nconst'])
                writer = models.Names.objects.filter(nconst=nameid)
            json = sr.serialize('json', writer)
            return Response(json, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format='json'):
        """
        tconst -- movie id
        nconst -- name id (should be blank)
        fullname -- name
        """
        print(request.data)
        titleid = request.data['tconst']
        name = request.data['fullname']
        lastname = models.Names.objects.latest('nconst')
        id = int(lastname.nconst[2:])
        id = "nm" + str(id + 1)
        namedata = {'nconst': id, 'primaryname': name}
        nameserializer = serializers.NameSerializer(data=namedata)
        if nameserializer.is_valid():
            done1 = nameserializer.save()
        else:
            return Response(nameserializer.errors, status=status.HTTP_400_BAD_REQUEST)
        writerdata = {'tconst': titleid, 'nconst': id}
        writerserializer = serializers.DirectorSerializer(data=writerdata)
        if writerserializer.is_valid():
            writerserializer.validated_data['tconst'] = models.Movies.objects.filter(titleid=titleid)[0]
            writerserializer.validated_data['nconst'] = models.Names.objects.filter(nconst=id)[0]
            done2 = writerserializer.save()
        else:
            return Response(writerserializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if done2 and done1:
            data = {'tconst': titleid, 'nconst': id, 'fullname': name}
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)


class Ratings(GenericAPIView):
    serializer_class = serializers.RatingsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def post(self, request):

        serializer = serializers.RatingsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['datetime'] = datetime.datetime.now(tz=timezone.utc)
            serializer.validated_data['userid'] = request.user.id
            userId = UserModel.objects.filter(id=serializer.validated_data['userid'])[0]
            titleId = models.Movies.objects.filter(titleid=serializer.validated_data['titleid'])[0]
            serializer.validated_data['userid'] = userId
            serializer.validated_data['titleid'] = titleId
            print(serializer.validated_data)
            movieratings = models.UsersRatings.objects.filter(titleid=serializer.validated_data['titleid'])
            rating = movieratings.filter(userid=serializer.validated_data['userid'])
            print(rating)
            if rating:
                rating = rating[0]
                oldrating = rating.rating
                rating.rating = serializer.validated_data['rating']
                rating.datetime = datetime.datetime.now(tz=timezone.utc)
                rating.save()
                titleId.avratingimdb = (float(titleId.avgratingimdb * titleId.numvotesimdb) - oldrating + rating.rating)/(titleId.numvotesimdb)
                titleId.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                saved = serializer.save()
                if saved:
                    titleId.avratingimdb = (float(titleId.avgratingimdb * titleId.numvotesimdb) +
                                            serializer.validated_data['rating']) / (titleId.numvotesimdb + 1)
                    titleId.numvotesimdb = titleId.numvotesimdb + 1
                    titleId.save()
                    return Response(status=status.HTTP_201_CREATED)
                else:
                    return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    name_param = openapi.Parameter('username', openapi.IN_QUERY, description="(optional)", type=openapi.TYPE_STRING)
    title_param = openapi.Parameter('titleId', openapi.IN_QUERY, description="(optional)", type=openapi.TYPE_STRING)
    get_200_response = openapi.Response('Getting ratings from database was successful',serializers.RatingsSerializer)
    @swagger_auto_schema(manual_parameters=[name_param,title_param], responses={200:get_200_response})
    def get(self,request,):
        ratings = models.UsersRatings.objects.all()
        if 'username' in request.GET :
            userId = UserModel.objects.filter(username=request.query_params['username'])
            if userId:
                ratings = ratings.filter(userid=userId[0].id)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        if 'titleId' in request.GET:
            ratings = ratings.filter(titleid=request.query_params['titleId'])

        json = sr.serialize('json',ratings)
        return Response(json,status=status.HTTP_200_OK)