from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from . import models

class FilmTest(APITestCase):
    def test_add_film(self):
        data = { "originaltitle":"The Terminator",
                 "polishtitle":"Elektroniczny morderca",
                 "genres":"Action,Sci-Fi",
                 "year":1984,
                 "avgratingimdb":8.0,
                 "numvotesimdb":82385,
                 "socialgrouplink":"null",
                 "sourcelink":"null"
        }

        response = self.client.post(reverse('movies'), data, format='json')
        movies = models.Movies.objects.latest('titleid')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(response.data['originaltitle'],data['originaltitle'])
        self.assertEqual(response.data['polishtitle'], data['polishtitle'])
        self.assertEqual(response.data['genres'], data['genres'])
        self.assertEqual(response.data['avgratingimdb'], data['avgratingimdb'])
        self.assertEqual(response.data['numvotesimdb'], data['numvotesimdb'])