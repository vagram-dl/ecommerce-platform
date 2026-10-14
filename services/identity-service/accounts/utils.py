import jwt
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken

def create_id_token(user, client = "ecommerce-platform"):
    base_token = AccessToken.for_user(user)
    payload = base_token.payload.copy()

    payload['sub'] = str(user.id)

    payload['email'] = getattr(user, 'email', '')
    payload['email_verified'] = getattr(user, 'is_email_verified', False)
    payload['preferred_username'] = getattr(user, 'username', '')

    if isinstance(client, str):
        payload['aud'] = client
    else:
        payload['aud'] = client.client_id

    custom_header = {
        "alg": "RS256",
        "typ": "JWT",
        "kid": "identity-service-rsa-2048"
    }

    private_key = settings.SIMPLE_JWT.get('SIGNING_KEY')

    encoded_token = jwt.encode(
        payload,
        private_key,
        algorithm="RS256",
        headers=custom_header
    )

    return encoded_token