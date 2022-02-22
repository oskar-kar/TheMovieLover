# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.auth import get_user_model
from django.db import models




User = get_user_model()

class Movies(models.Model):
    titleid = models.CharField(db_column='titleId', primary_key=True, max_length=12)  # Field name made lowercase.
    originaltitle = models.CharField(db_column='originalTitle', max_length=1000)  # Field name made lowercase.
    polishtitle = models.CharField(db_column='polishTitle', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    genres = models.CharField(max_length=50)
    year = models.SmallIntegerField()
    avgratingimdb = models.DecimalField(db_column='avgRatingImdb', max_digits=3, decimal_places=1)  # Field name made lowercase.
    numvotesimdb = models.BigIntegerField(db_column='numVotesImdb')  # Field name made lowercase.
    #avgratingour = models.FloatField(db_column='avgRatingOur')  # Field name made lowercase.
    #numvotesour = models.BigIntegerField(db_column='numVotesOur')  # Field name made lowercase.
    socialgrouplink = models.CharField(db_column='socialGroupLink', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    sourcelink = models.CharField(db_column='sourceLink', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    isnetflix = models.BooleanField(db_column='isNetflix')  # Field name made lowercase.
    ishbo = models.BooleanField(db_column='isHBO')  # Field name made lowercase.
    isamazonprime = models.BooleanField(db_column='isAmazonPrime')  # Field name made lowercase.
    tags = models.CharField(db_column='tags', max_length=2000)

    class Meta:
        managed = False
        db_table = 'movies'


class MoviesActors(models.Model):
    tconst = models.ForeignKey(Movies, models.DO_NOTHING, db_column='tconst')
    nconst = models.ForeignKey('Names', models.DO_NOTHING, db_column='nconst')
    connid = models.AutoField(db_column='connId', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'movies_actors'


class MoviesDirectors(models.Model):
    tconst = models.ForeignKey(Movies, models.DO_NOTHING, db_column='tconst')
    nconst = models.ForeignKey('Names', models.DO_NOTHING, db_column='nconst')
    connid = models.AutoField(db_column='connId', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'movies_directors'


class MoviesWriters(models.Model):
    tconst = models.ForeignKey(Movies, models.DO_NOTHING, db_column='tconst')
    nconst = models.ForeignKey('Names', models.DO_NOTHING, db_column='nconst')
    connid = models.AutoField(db_column='connId', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'movies_writers'


class Names(models.Model):
    nconst = models.CharField(primary_key=True, max_length=12)
    primaryname = models.CharField(db_column='primaryName', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'names'


class UsersRatings(models.Model):
    connid = models.AutoField(primary_key=True, db_column='connId')
    userid = models.ForeignKey(User, models.DO_NOTHING, db_column='userId', blank=True, null=False)  # Field name made lowercase.
    titleid = models.ForeignKey(Movies, models.DO_NOTHING, db_column='titleId', blank=True, null=False)  # Field name made lowercase.
    rating = models.IntegerField()
    datetime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'users_ratings'
