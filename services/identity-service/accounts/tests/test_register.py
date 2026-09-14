from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import User
from django.urls import reverse

class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')

    def test_register_user_success(self):
        payload = {
            'email':'newuser@ecommerce.com',
            'username':'newuser',
            'password':'StrongPassword123!'
        }

        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@ecommerce.com').exists())

        user = User.objects.get(email='newuser@ecommerce.com')
        self.assertNotEqual(user.password, 'StrongPassword123!')
        self.assertTrue(user.check_password('StrongPassword123!'))

    def test_register_user_weak_password(self):
        payload = {
            'email':'weak@ecommerce.com',
            'username':'weakuser',
            'password':'123456'
        }

        response = self.client.post(self.register_url, payload,format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email='weak@ecommerce.com').exists())