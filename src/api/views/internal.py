from rest_framework.views import APIView
from rest_framework import permissions, generics

from db.main.models import AppVersion
from api.backends import InternalAuthentication
from api.serializers import AppVersionSerializer


class InternalDebugThrowException(APIView):
    authentication_classes = (InternalAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        raise Exception('debug')


class InternalAppVersionListCreate(generics.ListCreateAPIView):
    authentication_classes = (InternalAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AppVersionSerializer

    def get_queryset(self):
        return AppVersion.objects.all()
