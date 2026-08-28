from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase,APIClient
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

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

