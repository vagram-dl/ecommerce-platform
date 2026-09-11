

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, LogoutSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from authlib.jose import JsonWebKey
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView


class RegisterView(APIView):
    permission_classes = []

    @transaction.atomic
    def post(self,request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    'id': user.id,
                    'email': user.email,
                    'message': 'User registered successfully'
                },
                status = status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = []


    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request':request})

        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'message': 'Login successful'
                },
                status = status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self,request):
        serializer = LogoutSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JWKSView(APIView):
    permission_classes = []

    def get(self,request):
        public_key_pem = settings.SIMPLE_JWT['VERIFYING_KEY']
        jwk = JsonWebKey.import_key(public_key_pem)

        jwk_data = jwk.as_dict()
        jwk_data['kid'] = 'identity-service-rsa-2048'
        jwk_data['use'] = 'sig'
        jwk_data['alg'] = 'RS256'

        return JsonResponse({"keys": [jwk_data]})

