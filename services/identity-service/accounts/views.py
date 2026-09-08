

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, LogoutSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
import base64
from django.conf import settings
from cryptography.hazmat.primitives import serialization
from django.http import JsonResponse


class RegisterView(APIView):
    permission_classes = []

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

    def post(self,request):
        serializer = LogoutSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JWKSView(APIView):
    permission_classes = []

    def get(self, request):
        public_key_pem = settings.SIMPLE_JWT['VERIFYING_KEY']
        public_key = serialization.load_pem_public_key(public_key_pem)
        public_numbers = public_key.public_numbers()

        def int_to_base64url(n):
            byte_length = (n.bit_length() + 7) // 8
            return base64.urlsafe_b64encode(n.to_bytes(byte_length, 'big')).rstrip(b'=').decode('ascii')
        jwk = {
            "kty": "RSA",
            "use": "sig",
            "n": int_to_base64url(public_numbers.n),
            "e": int_to_base64url(public_numbers.e),
            "kid": "identity-service-rsa-2048"
        }

        return JsonResponse({"keys": [jwk]})