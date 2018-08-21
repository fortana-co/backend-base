from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from db.users.models import PublicUser, UserToken
from api.backends import UserAuthentication
from api.serializers import UserSerializer, UserTokenSerializer
from api.serializers import PasswordSerializer, PasswordTokenSerializer, SendSetPasswordEmailSerializer


class AccountSendSetPasswordEmail(APIView):
    """Send set password email to user, identified by email.
    """
    throttle_scope = 'authentication'

    def post(self, request, *args, **kwargs):
        serializer = SendSetPasswordEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = PublicUser.objects.filter(email=email).first()
        if user is not None:
            if not user.is_active:
                return Response({'error': 'user not active'})
            user.send_set_password_email()
        return Response({'email': email})


class AccountSetPasswordWithToken(APIView):
    """Set user's password, authenticating with token.
    """
    throttle_scope = 'authentication'

    def post(self, request, *args, **kwargs):
        serializer = PasswordTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(PublicUser, set_password_token=serializer.validated_data['token'])
        if not user.set_password_token_created or user.set_password_token_created < timezone.now() - timedelta(days=3):
            return Response({'error': 'This token has expired'}, status=403)
        user.set_password(serializer.validated_data['password'])
        user.set_password_token = ''
        user.save()
        if serializer.validated_data['created']:
            user.send_training_email()
        return Response({'id': user.pk})


class AccountToken(APIView):
    """View for obtaining an auth token by posting a valid (email, password).
    """
    throttle_scope = 'authentication'

    def post(self, request, *args, **kwargs):
        serializer = UserTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = UserToken.objects.get_or_create(user=user)
        return Response({'token': token.key, 'id': user.pk, 'organization_id': user.organization.id})


class AccountDeleteToken(APIView):
    authentication_classes = (UserAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    throttle_scope = 'authentication'

    def post(self, request, *args, **kwargs):
        try:
            token = self.request.user.auth_token
        except ObjectDoesNotExist:
            return Response({}, status=400)
        else:
            token.delete()
            return Response({})


class AccountSetPassword(APIView):
    """Set org user's password. Requires passing old password for security.
    """
    authentication_classes = (UserAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    throttle_scope = 'authentication'

    def post(self, request, *args, **kwargs):
        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(serializer.validated_data['old_password']):
            return Response({}, status=400)
        request.user.set_password(serializer.validated_data['password'])
        request.user.save()
        return Response({'id': request.user.pk})


class AccountMe(generics.RetrieveUpdateAPIView):
    authentication_classes = (UserAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)
