from pydoc import resolve
from tkinter import image_types

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase,APIClient
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from unittest.mock import patch,MagicMock
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from jwt.algorithms import RSAAlgorithm
from django.contrib.auth import get_user_model



UserModel = get_user_model()

class CustomJWKSAuthTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_private_key = rsa.generate_private_key(public_exponent=65537,key_size=2048)
        cls.test_public_key = cls.test_private_key.public_key()

        cls.private_key_pem = cls.test_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format = serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        cls.public_key_jwk_dict = RSAAlgorithm.to_jwk(cls.test_public_key, as_dict=True)
        cls.kid = 'test-kid-123'
        cls.public_key_jwk_dict['kid'] = cls.kid
        cls.public_key_jwk_dict['use'] = 'sig'
        cls.public_key_jwk_dict['alg'] = 'RS256'

    def setUp(self):
        self.user = UserModel.objects.create_user(
            id=99,
            username='jwks_user',
            email='jwks@example.com'
        )
        self.user.set_unusable_password()
        self.user.save()
        self.test_url = '/api/test-auth/'

    def _create_custom_token(self, payload_overrides=None, header_overrides=None):
        now = datetime.utcnow()
        payload = {
            'sub': str(self.user.id),
            'email': self.user.email,
            'preferred_username': self.user.username,
            'aud': 'ecommerce-platform',
            'exp': now + timedelta(minutes=5),
            'iat': now,
        }
        if payload_overrides:
            payload.update(payload_overrides)

        header = {'alg': 'RS256', 'typ': 'JWT', 'kid': self.kid}
        if header_overrides:
            header.update(header_overrides)

        return jwt.encode(payload, self.private_key_pem, algorithm='RS256', headers=header)

    def _mock_jwks_response(self):
        return {'keys': [self.public_key_jwk_dict]}

    @patch('shop_project.jwks_cache.requests.get')
    def test_valid_custom_token(self,mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = self._mock_jwks_response()
        mock_response.raise_for_status = lambda :None
        mock_get.return_value = mock_response

        token = self._create_custom_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('УСПЕХ', response.data['message'])
        self.assertEqual(response.data['user_id'], self.user.id)

    @patch('shop_project.jwks_cache.requests.get')
    def test_expired_token(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = self._mock_jwks_response()
        mock_response.status_code = 200
        mock_response.raise_for_status = lambda: None
        mock_get.return_value = mock_response

        payload_overrides = {
            'exp': datetime.utcnow() - timedelta(seconds=10),
            'iat': datetime.utcnow() - timedelta(minutes=10)
        }
        token = self._create_custom_token(payload_overrides=payload_overrides)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.get(self.test_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Токен истек', response.data['detail'])

    @patch('shop_project.jwks_cache.requests.get')
    def test_wrong_audience(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = self._mock_jwks_response()
        mock_response.status_code = 200
        mock_response.raise_for_status = lambda :None
        mock_get.return_value = mock_response

        payload_overrides = {'aud':'wrong-service'}
        token = self._create_custom_token(payload_overrides=payload_overrides)
        self.client.credentials(HTTP_AUTHORIZATION = f'Bearer {token}')

        response = self.client.get(self.test_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Audience doesn't match", response.data['detail'])

    @patch('shop_project.jwks_cache.requests.get')
    def test_missing_kid_in_header(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = self._mock_jwks_response()
        mock_response.status_code = 200
        mock_response.raise_for_status = lambda : None
        mock_get.return_value = mock_response

        header_overrides = {'kid': ''}
        token = self._create_custom_token(header_overrides=header_overrides)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.get(self.test_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Ошибка аутентификации')


class JWTAuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username = 'testuser',
            password = 'testpass123',
            email = 'test@example.com'
        )

        self.token_url = reverse('token_obtain_pair')
        self.token_refresh_url = reverse('token_refresh')
        self.protected_url = reverse('profile')
        self.client = APIClient()

    def test_obtain_token_valid_credentials(self):
        data = {
            'username' : 'testuser',
            'password' : 'testpass123'
        }

        response = self.client.post(self.token_url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertIn('access',response.data)
        self.assertIn('refresh',response.data)

    def test_obtain_token_invalid_password(self):
        data = {
            'username' : 'testuser',
            'password' : 'wrongpassword'
        }

        response = self.client.post(self.token_url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

        self.assertNotIn('access',response.data)
        self.assertNotIn('refresh',response.data)

        self.assertIn('detail',response.data)
        self.assertEqual(
            response.data['detail'],
            'No active account found with the given credentials'
        )

    def test_obtain_token_invalid_username(self):
        data = {
            'username' : 'nonexistent',
            'password' : 'textpass123'
        }

        response = self.client.post(self.token_url,data,format = 'json')
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        
    def test_refresh_token_valid(self):
        auth_data = {
            'username' : 'testuser',
            'password' : 'testpass123'
        }

        auth_response = self.client.post(self.token_url,auth_data,format='json')
        refresh_token = auth_response.data['refresh']

        refresh_data = {
            'refresh':refresh_token
        }

        response = self.client.post(self.token_refresh_url,refresh_data,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertIn('access',response.data)
        self.assertNotIn('refresh',response.data)

    def test_refresh_token_invalid(self):
        refresh_data = {
            'refresh' : 'invalid.token.string'
        }

        response = self.client.post(self.token_refresh_url,refresh_data,format='json')
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

