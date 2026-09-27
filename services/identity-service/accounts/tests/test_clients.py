from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.clients import create_customer_in_shop

User = get_user_model()

class CreateCustomerInShopTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username = 'testuser',
            email = 'test@example.com',
            password = 'TestPass123!'
        )
    @patch('accounts.clients.requests.post')
    def test_create_customer_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': 1,
            'user_id' : self.user.id,
            'email':self.user.email
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = create_customer_in_shop(self.user)

        self.assertIsNotNone(result)
        self.assertEqual(result['id'],1)
        self.assertEqual(result['user_id'], self.user.id)
