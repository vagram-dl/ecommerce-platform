from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class JWKSViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.jwks_url = reverse("jwks")

    def test_jwks_return_keys(self):
        response = self.client.get(self.jwks_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertIn("keys", response_data)
        self.assertTrue(len(response_data["keys"]) > 0)

    def test_jwks_returns_correct_jwk_structure(self):
        response = self.client.get(self.jwks_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        keys = response_data["keys"]

        self.assertEqual(len(keys), 1)

        jwk = keys[0]

        self.assertIn("kid", jwk)
        self.assertIn("use", jwk)
        self.assertIn("alg", jwk)
        self.assertIn("kty", jwk)
        self.assertIn("n", jwk)
        self.assertIn("e", jwk)

        self.assertEqual(jwk["kid"], "identity-service-rsa-2048")
        self.assertEqual(jwk["use"], "sig")
        self.assertEqual(jwk["alg"], "RS256")
        self.assertEqual(jwk["kty"], "RSA")
