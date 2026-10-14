import time
import threading
import requests
from django.conf import settings
from jwt.algorithms import RSAAlgorithm

class JWKSCache:
    _instance = None
    _lock = threading.Lock()

    JWKS_URL = getattr(
        settings,
        'IDENTITY_SERVICE_JWKS_URL',
        'http://localhost:8000/.well-known/jwks.json'
    )

    TTL = 8 * 3600

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(JWKSCache,cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._keys = {}
        self._last_fetched = 0
        self._fetch_lock = threading.Lock()

    def get_public_key(self, kid:str):
        if self._is_expired() or kid not in self._keys:
            self._refresh_keys()
        return self._keys.get(kid)

    def _is_expired(self)->bool:
        return (time.time() - self._last_fetched) > self.TTL

    def _refresh_keys(self):
        with self._fetch_lock:
            if not self._is_expired() and self._keys:
                return
            try:
                response = requests.get(self.JWKS_URL, timeout=5)
                response.raise_for_status()

                jwks_data = response.json()
                new_keys = {}
                for key_data in jwks_data.get('keys',[]):
                    kid = key_data.get('kid')
                    if kid:
                        new_keys[kid] = RSAAlgorithm.from_jwk(key_data)
                self._keys = new_keys
                self._last_fetched = time.time()

            except requests.exceptions.RequestException as e:
                print(f"Error fetching JWKS:{e}")