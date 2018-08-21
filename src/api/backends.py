import os

from django.contrib.auth.models import User

from rest_framework import authentication
from rest_framework import exceptions

from db.users.models import UserToken


class UserAuthentication(authentication.BaseAuthentication):
    """Authentication using bearer token in AUTHORIZATION header.
    """
    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION')
        if not auth:
            return None
        try:
            _, token = auth.split()
        except:
            return None

        try:
            tkn = UserToken.objects.get(key=token)
        except UserToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('invalid_token')
        if not tkn.user.is_active:
            raise exceptions.AuthenticationFailed('invalid_token')

        return (tkn.user, 'PublicUser')


class InternalAuthentication(authentication.BaseAuthentication):
    """Allows processes that run on our servers to authenticate with our API.
    """
    def authenticate(self, request):
        key = os.getenv('CUSTOM_INTERNAL_AUTH_KEY')
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        try:
            _, token = auth.split()
        except:
            return None

        if not key or key != token:
            return None
        return (User(), 'InternalUser')
