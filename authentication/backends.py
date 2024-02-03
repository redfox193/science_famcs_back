import jwt

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import User


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Token'

    def authenticate(self, request):
        request.user = None

        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1 or len(auth_header) > 2:
            return None

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if not prefix.lower().__eq__(auth_header_prefix):
            return None

        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        try:
            payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
        except Exception:
            msg = 'Unable to decode token.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            msg = 'User, related to this token, does not exist.'
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = 'User is not active.'
            raise exceptions.AuthenticationFailed(msg)

        return user, token