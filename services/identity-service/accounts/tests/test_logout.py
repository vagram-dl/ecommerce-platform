from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class LogoutViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.logout_url = reverse('logout')

        self.user = User.objects.create_user(
            email = 'logouttest@ecommerce.com',
            username = 'logouttest',
            password = 'StrongPassword123!'
        )

        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh_token.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_logout_success(self):
        payload = {
            'refresh': str(self.refresh_token)
        }

        response = self.client.post(self.logout_url, payload,format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_invalid_token(self):
        payload = {
            'refresh' : 'this_is_a_fake_and_invalid_token_string'
        }

        response = self.client.post(self.logout_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)