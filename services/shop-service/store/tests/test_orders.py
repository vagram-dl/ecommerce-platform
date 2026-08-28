from django.test import TestCase,Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Product,Category

class OrderViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username = 'testuser',
            password = 'testpass123'
        )

        self.orders_url = reverse('orders')
        self.client = Client()

    def test_orders_view_requires_login(self):
        response = self.client.get(self.orders_url)
        self.assertIn('login',response.url)
        self.assertTrue(response.url.endswith(f'?next={self.orders_url}'))

    def test_orders_view_authenticated(self):
        self.client.login(username='testuser',password='testpass123')
        response = self.client.get(self.orders_url)

    def test_orders_view_empty(self):
        self.client.login(username='testuser',password = 'testpass123')
        response = self.client.get(self.orders_url)

        self.assertNotContains(response,"order-table")


        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'store/orders.html')


