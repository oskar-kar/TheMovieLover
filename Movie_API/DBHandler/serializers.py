from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from . import models



# -------/MOVIES/--------#


class MoviesSerializer(serializers.ModelSerializer):
    titleid = serializers.CharField(max_length=12, allow_blank=True, required=False)  # Field name made lowercase.
    originaltitle = serializers.CharField(max_length=1000, allow_blank=True, required=True, validators=[UniqueValidator(queryset=models.Movies.objects.all())])  # Field name made lowercase.
    polishtitle = serializers.CharField(max_length=1000, allow_blank=True, required=True, validators=[UniqueValidator(queryset=models.Movies.objects.all())])  # Field name made lowercase.
    genres = serializers.CharField(max_length=50, allow_blank=True, required=True)
    year = serializers.FloatField(allow_null=True, required=False)
    avgratingimdb = serializers.DecimalField(max_digits=3, decimal_places=1, allow_null=True, required=True)  # Field name made lowercase.
    numvotesimdb = serializers.FloatField(allow_null=True, required=True)  # Field name made lowercase.
    socialgrouplink = serializers.CharField(max_length=2000, allow_blank=True, required=False)  # Field name made lowercase.
    sourcelink = serializers.CharField(max_length=2000, allow_blank=True, required=False)  # Field name made lowercase.
    # isnetflix = serializers.BooleanField()  # Field name made lowercase.
    # ishbo = serializers.BooleanField()  # Field name made lowercase.
    # isamazonprime = serializers.BooleanField()  # Field name made lowercase.


    class Meta:
        model = models.Movies
        optional_fields = ['titleid', 'year', 'avgratingimdb', 'numvotesimdb', 'socialgrouplink', 'sourcelink', ]
        fields = ('titleid', 'originaltitle', 'polishtitle', 'genres', 'year', 'avgratingimdb', 'numvotesimdb', 'socialgrouplink', 'sourcelink')

class ActorSerializer(serializers.ModelSerializer):
    tconst = serializers.CharField(max_length=12, allow_blank=True)
    nconst = serializers.CharField(max_length=12, allow_blank=True)

    class Meta:
        model = models.MoviesActors
        fields = ('tconst', 'nconst')

class DirectorSerializer(serializers.ModelSerializer):
    tconst = serializers.CharField(max_length=12, allow_blank=True)
    nconst = serializers.CharField(max_length=12, allow_blank=True)

    class Meta:
        model = models.MoviesDirectors
        fields = ('tconst', 'nconst', 'fullname')

class WriterSerializer(serializers.ModelSerializer):
    tconst = serializers.CharField(max_length=12, allow_blank=True)
    nconst = serializers.CharField(max_length=12, allow_blank=True)

    class Meta:
        model = models.MoviesWriters
        fields = ('tconst', 'nconst')

class NameSerializer(serializers.ModelSerializer):
    nconst = serializers.CharField(max_length=12, allow_blank=True)
    primaryname = serializers.CharField(max_length=64, allow_blank=True ,validators=[UniqueValidator(queryset=models.Names.objects.all())])

    class Meta:
        model = models.Names
        fields = ('nconst', 'primaryname')

class PeopleSerializer(serializers.ModelSerializer):
    tconst = serializers.CharField(max_length=12, allow_blank=True)
    nconst = serializers.CharField(max_length=12, allow_blank=True)
    fullname = serializers.CharField(max_length=64, allow_blank=True,
                                        validators=[UniqueValidator(queryset=models.Names.objects.all())])
    class Meta:
        model = models.Names
        fields = ('tconst', 'nconst', 'fullname')

class RatingsSerializer(serializers.ModelSerializer):
    userid = serializers.CharField(max_length=12, required=False)
    titleid = serializers.CharField(max_length=12)
    rating = serializers.IntegerField(min_value=1, max_value=10)
    datetime = serializers.DateTimeField(allow_null=True, required=False)
    class Meta:
        model = models.UsersRatings
        fields = ('userid', 'titleid', 'rating', 'datetime')