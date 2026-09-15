from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import User

class LoginViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')

        self.user = User.objects.create_user(
            email = 'logintest@ecommerce.com',
            username='logintest',
            password='StrongPassword123!'
        )

    def test_login_success(self):
        payload = {
            'email':'logintest@ecommerce.com',
            'password':'StrongPassword123!'
        }

        response = self.client.post(self.login_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        payload = {
            'email':'logintest@ecommerce.com',
            'test':'WrongPassword123!'
        }

        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)