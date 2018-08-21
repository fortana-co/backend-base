from rest_framework import serializers

from db.users.models import PublicUser
from .base import authenticate, Serializer, ModelSerializer


class UserTokenSerializer(Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email').strip()
        password = attrs.get('password').strip()

        user = authenticate(PublicUser, email, password)
        if not user:
            raise serializers.ValidationError('Unable to log in with provided credentials')

        attrs['user'] = user
        return attrs


class SendSetPasswordEmailSerializer(Serializer):
    email = serializers.EmailField()


class PasswordSerializer(Serializer):
    old_password = serializers.CharField(allow_blank=False, trim_whitespace=True)
    password = serializers.CharField(min_length=8, max_length=None, allow_blank=False, trim_whitespace=True)


class PasswordTokenSerializer(Serializer):
    password = serializers.CharField(min_length=8, max_length=None, allow_blank=False, trim_whitespace=True)
    token = serializers.CharField(min_length=20, max_length=None, allow_blank=False, trim_whitespace=True)
    created = serializers.BooleanField(required=False, default=False)


class UserSerializer(ModelSerializer):
    class Meta:
        model = PublicUser
        fields = ('email', 'full_name', 'first_name', 'surnames', 'is_active', 'is_mainuser', 'id')
        read_only_fields = ('email', 'is_active', 'is_mainuser', 'full_name', 'id')
