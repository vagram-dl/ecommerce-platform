from rest_framework_simplejwt.tokens import AccessToken

def create_id_token(user,client):
    token = AccessToken.for_user(user)

    token['email'] = user.email
    token['email_verified'] = getattr(user, 'is_email_verified',False)
    token['preferred_username'] = user.username

    token['aud'] = client.client_id
    return str(token)