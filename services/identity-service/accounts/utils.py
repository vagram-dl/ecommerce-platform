from rest_framework_simplejwt.tokens import AccessToken

def create_id_token(user):
    token = AccessToken.for_user(user)

    token['email'] = user.email
    token['email_verified'] = user.is_email_verified
    token['preferred_username'] = user.username

    token['aud'] = 'ecommerce-frontend-app'
    return str(token)