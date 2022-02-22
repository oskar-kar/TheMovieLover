import requests
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from django.core import serializers as sr
from DBHandler import models
from DBHandler import serializers
# Create your views here.


class Recommendations(GenericAPIView):
    serializer_class = serializers.MoviesSerializer
    permission_classes = [permissions.IsAuthenticated]

    get_200_response = openapi.Response('Getting recommendations from database was successful', serializers.MoviesSerializer)
    get_401_response = openapi.Response('User\'s token has expired or it wasn\'t present in the headers')
    get_503_response = openapi.Response('Couldn\'t get recommendations (server-side)')
    @swagger_auto_schema(operation_description='Returns movies recommended for the user identified by the token',responses={200: get_200_response, 401:get_401_response, 503:get_503_response})
    def get(self, request):
        user = request.user.id
        try:
            resp = requests.get('http://127.0.0.1:8001/recommendations',params={'userId': user},timeout=2)
            print(resp.status_code)
            if(resp.status_code == 200):
                print(resp.json())
                return Response(resp.json(),status=status.HTTP_200_OK)
            recommended = models.Movies.objects.order_by('-avgratingimdb')[:8]
            json = sr.serialize('json', recommended)
            return Response(json, status=status.HTTP_200_OK)
        except:
            recommended = models.Movies.objects.order_by('-avgratingimdb')[:8]
            json = sr.serialize('json', recommended)
            return Response(json, status=status.HTTP_200_OK)
        #TODO Connect with Recommendation System API