from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

class JWKSViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.jwks_url = reverse('jwks')

    def test_jwks_return_keys(self):
        response = self.client.get(self.jwks_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertIn('keys',response_data)
        self.assertTrue(len(response_data['keys'])>0)