import jwt
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions

from shop_project.jwks_cache import JWKSCache

User = get_user_model()


class JWKSAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")

        if not auth_header or not auth_header.startswith("Bearer"):
            return None
        token = auth_header.split(" ")[1]

        try:
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            if not kid:
                raise exceptions.AuthenticationFailed('В токене отсутсвует "kid" ')
            public_key = JWKSCache().get_public_key(kid)

            if not public_key:
                raise exceptions.AuthenticationFailed("Недействительный или истекший ключ (kid)")

            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience="ecommerce-platform",
                options={"require": ["exp", "iat", "sub"]},
            )

            user_id = payload.get("sub") or payload.get("user_id")

            if not user_id:
                raise exceptions.AuthenticationFailed("В токене отсутсвует ID пользователя")
            user, created = User.objects.get_or_create(
                id=user_id,
                defaults={
                    "email": payload.get("email", ""),
                    "username": payload.get("preferred_username", f"user_{user_id}"),
                },
            )
            if created:
                user.set_unusable_password()
                user.save()
            return (user, token)

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Токен истек")
        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(f"Недействительный токен: {str(e)}")
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("Пользователь не найден в shop-service")
        except Exception as e:
            print(f"Ошибка аутентификации: {e}")
            raise exceptions.AuthenticationFailed("Ошибка аутентификации")

    def authenticate_header(self, request):
        return 'Bearer realm= "api" '
