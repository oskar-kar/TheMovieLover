from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import GenericAPIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from . import serializers

# Create your views here.
# -----/Registration/------#

class UserCreate(GenericAPIView):
    """
    Creates the user.
    """
    serializer_class = serializers.UserSerializer

    def post(self, request, format='json'):

        serializer = serializers.UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------/Token Logout/------------#
class LogoutView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            print(request.auth)
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

