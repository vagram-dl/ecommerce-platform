from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import User, OIDCClient, AuthorizationCode
from django.utils import timezone
from datetime import timedelta

class OIDCFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.token_uri= reverse('token')
        self.userinfo = reverse('userinfo')

        self.user = User.objects.create_user(
            email = 'oidctest@ecommerce.com',
            username = 'oidctest',
            password = 'StrongPassword123'
        )


        self.client_app = OIDCClient.objects.create(
            client_id = 'test-client-123',
            client_secret = 'super-secret-key',
            redirect_uri = 'http://localhost:3000/callback',
            owner = self.user,
            is_active = True
        )

    def _create_valid_auth_code(self):
        return AuthorizationCode.objects.create(
            client = self.client_app,
            user = self.user,
            redirect_uri = 'http://localhost:3000/callback',
            expires_at = timezone.now() + timedelta(minutes=5)
        )

    def test_token_exchange_success(self):
        auth_code = self._create_valid_auth_code()

        payload = {
            'grant_type' : 'authorization_code',
            'code': auth_code.code,
            'client_id':'test-client-123',
            'client_secret':'super-secret-key',
            'redirect_uri':'http://localhost:3000/callback'
        }

        response = self.client.post(self.token_uri, payload, format='json')

        print("\n" + "=" * 50)
        print("ОТВЕТ СЕРВЕРА (TokenView):", response.data)
        print("=" * 50 + "\n")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token',response.data)
        self.assertIn('refresh_token',response.data)
        self.assertIn('id_token', response.data)
        self.assertEqual(response.data['token_type'],'Bearer')

    def test_token_exchange_replay_attack(self):
        auth_code = self._create_valid_auth_code()
        payload = {
            'grant_type': 'authorization_code',
            'code': auth_code.code,
            'client_id': 'test-client-123',
            'client_secret': 'super-secret-key',
            'redirect_uri': 'http://localhost:3000/callback'
        }

        response1 = self.client.post(self.token_uri, payload, format = 'json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        response2 = self.client.post(self.token_uri,payload,format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response2.data)

    def test_userinfo_with_valid_token(self):
        auth_code = self._create_valid_auth_code()
        token_payload = {
            'grant_type': 'authorization_code',
            'code': auth_code.code,
            'client_id': 'test-client-123',
            'client_secret': 'super-secret-key',
            'redirect_uri': 'http://localhost:3000/callback'
        }
        token_response = self.client.post(self.token_uri, token_payload, format='json')
        access_token = token_response.data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION = f'Bearer {access_token}')
        userinfo_response = self.client.get(self.userinfo)

        self.assertEqual(userinfo_response.status_code, status.HTTP_200_OK)
        self.assertEqual(userinfo_response.data['sub'],str(self.user.id))
        self.assertEqual(userinfo_response.data['email'],self.user.email)