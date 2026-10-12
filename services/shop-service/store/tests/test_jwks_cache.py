import time
from unittest import TestCase
from unittest.mock import patch,MagicMock

import requests.exceptions

from shop_project.jwks_cache import JWKSCache

class TestJWKSCache(TestCase):
    def setUp(self):
        JWKSCache._instance = None

    def tearDown(self):
        JWKSCache._instance = None

    def test_singleton_pattern(self):
        cache1 = JWKSCache()
        cache2 = JWKSCache()

        self.assertIs(cache1,cache2, "Должен возвращаться один и тот же экземпляр")

    @patch('shop_project.jwks_cache.requests.get')
    def test_initial_fetch_populates_cache(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'keys':[
                {'kid':'key-123', 'kty':'RSA','n':'abc','e':'def'},
                {'kid':'key-456','kty':'RSA','n':'ghi','e':'jkl'}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        cache = JWKSCache()
        cache._keys = {}
        cache._last_fetched = 0

        key = cache.get_public_key('key-123')

        self.assertIsNotNone(key,"Ключ должен быть найден")
        self.assertEqual(key['kid'],'key-123')
        mock_get.assert_called_once()

    @patch('shop_project.jwks_cache.requests.get')
    def test_cache_hit_no_http_request(self,mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'keys': [{'kid':'key-123','kty':'RSA','n':'abc','e':'def'}]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        cache = JWKSCache()
        cache._keys = {}
        cache._last_fetched = time.time()

        key1 = cache.get_public_key('key-123')
        self.assertIsNotNone(key1)
        mock_get.assert_called_once()

        mock_get.reset_mock()

        key2 = cache.get_public_key('key-123')
        self.assertIsNotNone(key2)
        self.assertEqual(key1,key2)
        mock_get.assert_not_called()

    @patch('shop_project.jwks_cache.requests.get')
    @patch('shop_project.jwks_cache.time.time')
    def test_ttl_expiration_refreshes_cache(self, mock_time, mock_get):
        mock_time.return_value = 1000000

        mock_response = MagicMock()
        mock_response.json.return_value = {
            'keys': [{'kid':'key-123','kty':'RSA','n':'abc','e':'def'}]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        cache = JWKSCache()
        cache_keys = {}
        cache._last_fetched = 1000000

        key1 = cache.get_public_key('key-123')
        self.assertIsNotNone(key1)
        mock_get.assert_called_once()
        mock_get.reset_mock()

        mock_time.return_value = 1000000 + (9 * 3600)

        key2 = cache.get_public_key('key-123')
        self.assertIsNotNone(key2)
        mock_get.assert_called_once()

    @patch('shop_project.jwks_cache.requests.get')
    def test_graceful_degradation_on_network_error(self, mock_get):
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'keys': [{'kid': 'key-123', 'kty': 'RSA', 'n': 'abc', 'e': 'def'}]
            }

            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            cache = JWKSCache()
            cache._keys = {}
            cache._last_fetched = time.time()

            key1 = cache.get_public_key('key-123')
            self.assertIsNotNone(key1)

            mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

            cache._last_fetched = 0
            key2 = cache.get_public_key('key-123')

            self.assertIsNotNone(key2, "Старый ключ должен сохраниться при ошибке сети")
            self.assertEqual(key2['kid'],'key-123')

    @patch('shop_project.jwks_cache.requests.get')
    def test_unknown_kid_triggers_refresh(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'keys':[{'kid':'key-123', 'kty':'RSA','n':'abc','e':'def'}]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        cache = JWKSCache()
        cache._keys = {}
        cache._last_fetched = time.time()

        key = cache.get_public_key('unknown-key')

        mock_get.assert_called_once()
        self.assertIsNone(key, "Неизвестный ключ должен вернуть None")