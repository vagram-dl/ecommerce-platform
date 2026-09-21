

from rest_framework import status
from rest_framework.response import Response


from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, LogoutSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from authlib.jose import JsonWebKey
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from .throttles import AuthRateThrottling
from .utils import create_id_token
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta
import uuid


from .models import OIDCClient, AuthorizationCode


class RegisterView(APIView):
    permission_classes = []
    throttle_classes = [AuthRateThrottling]

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
    throttle_classes = [AuthRateThrottling]


    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request':request})

        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            id_token = create_id_token(user)

            return Response(
                {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'id_token': id_token,
                    'message': 'Login successful'
                },
                status = status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

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

class AuthorizeView(LoginRequiredMixin, APIView):
    def get(self, request):
        client_id = request.GET.get('client_id')
        redirect_uri = request.GET.get('redirect_uri')
        response_type = request.GET.get('response_type')

        if response_type != 'code':
            return Response({'error': 'Unsupported response_type'},status =400)

        try:
            client = OIDCClient.objects.get(client_id=client_id)
        except OIDCClient.DoesNotExist:
            return Response({'error': 'Invalid client_id'},status=400)

        if not client.is_active:
            return Response({'error':'Client is not active'},status=400)

        if redirect_uri != client.redirect_uri:
            return Response({'error':'Invalid redirect_uri'}, status=400)

        auth_code = AuthorizationCode.objects.create(
            client = client,
            user = request.user,
            redirect_uri = redirect_uri
        )

        return redirect(f"{redirect_uri}?code={auth_code.code}")

class TokenView(APIView):   
    def post(self, request):
        grant_type = request.data.get('grant_type')
        code = request.data.get('code')
        client_id = request.data.get('client_id')
        client_secret = request.data.get('client_secret')
        redirect_uri = request.data.get('redirect_uri')

        if grant_type != 'authorization_code':
            return Response({'error':'Unsupported grant_type'}, status=400)

        try:
            client = OIDCClient.objects.get(client_id=client_id)
        except OIDCClient.DoesNotExist:
            return Response({'error':'Invalid client_id'},status=400)

        if client_secret != client.client_secret:
            return Response({'error':'Invalid client_secret'},status=401)

        try:
            auth_code = AuthorizationCode.objects.get(code=code)
        except AuthorizationCode.DoesNotExist:
            return Response({'error':'Invalid code'},status=400)

        if not auth_code.is_valid:
            return Response({'error':'Code is expired or already used'},status=400)

        if auth_code.client != client or auth_code.redirect_uri != redirect_uri:
            return Response({'error':'Code mismatch'},status=400)

        auth_code.is_used = True
        auth_code.save()

        refresh = RefreshToken.for_user(auth_code.user)
        id_token = create_id_token(auth_code.user, client)

        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token':str(refresh),
            'id_token':id_token,
            'token_type':'Bearer',
            'expires_in': 900,
        })
