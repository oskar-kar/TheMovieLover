"""
WSGI config for Movie_Recommender project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""
import pandas as pd
from DBHandler import models
from . import populateDB
from . import recommender
from Movie_Recommender_App import views
import os
from django_pandas.io import read_frame
from django.core.wsgi import get_wsgi_application
from django.core import serializers as sr

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Movie_Recommender.settings')

application = get_wsgi_application()

movie = models.Movies.objects.get(originaltitle="Toy Story")

#if movie.tags is None or movie.tags == "":
#populateDB.populate_db()

RECOMMENDER = recommender.Recommender()