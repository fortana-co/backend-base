from rest_framework import serializers

from db.main.models import AppVersion


class EagerLoadingMixin:
    @classmethod
    def setup_eager_loading(cls, queryset):
        # foreign key and one to one
        if hasattr(cls, '_SELECT_RELATED_FIELDS'):
            queryset = queryset.select_related(*cls._SELECT_RELATED_FIELDS)
        # many to many, many to one
        if hasattr(cls, '_PREFETCH_RELATED_FIELDS'):
            queryset = queryset.prefetch_related(*cls._PREFETCH_RELATED_FIELDS)
        # each element in this list must be a function that returns a `Prefetch` instance
        if hasattr(cls, '_PREFETCH_FUNCTIONS'):
            queryset = queryset.prefetch_related(*[func() for func in cls._PREFETCH_FUNCTIONS])
        return queryset


class Serializer(serializers.Serializer, EagerLoadingMixin):
    pass


class ModelSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    pass


class AppVersionSerializer(serializers.ModelSerializer):
    git_hash_short = serializers.ReadOnlyField()

    class Meta:
        model = AppVersion
        fields = '__all__'


def authenticate(model, email, password):
    if not email or not password:
        return None
    user = model.objects.filter(email=email).first()
    if not user or not user.is_active or not user.check_password(password):
        return None
    return user
