from django.test import TestCase,Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Product,Category

class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username = 'testuser',
            password = 'testpass123',
            email = 'test@example.com'
        )

        self.another_user = User.objects.create_user(
            username = 'anotheruser',
            password='testpass123',
            email = 'another@example.com'
        )

        self.profile_url = reverse('profile')
        self.client = Client()

    def test_profile_view_requires_login(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code,302)
        self.assertIn('login',response.url)

    def test_profile_view_authenticated(self):
        self.client.login(username = 'testuser',password='testpass123')
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'store/profile.html')
        self.assertContains(response,'testuser')
