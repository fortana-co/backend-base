from django.conf import settings
from django.conf.urls import url

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from api import views


docs_cache = 60 * 60
if not settings.ENVIRONMENT == 'production':
    docs_cache = 0

schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version='v1',
        description="REST API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# `cache_page` also sets `Cache-Control: max-age=<seconds>` in response headers
urlpatterns = [
    # autodoc
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=docs_cache), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=docs_cache), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=docs_cache), name='schema-redoc'),

    # internal endpoints
    url(r'^internal/app_versions/$', views.InternalAppVersionListCreate.as_view()),
    url(r'^internal/debug/throw_exception/$', views.InternalDebugThrowException.as_view()),

    # public endpoints
    url(r'^$', views.api_root),

    # account endpoints
    url(r'^account/token/$', views.AccountToken.as_view()),
    url(r'^account/delete_token/$', views.AccountDeleteToken.as_view()),
    url(r'^account/set_password/$', views.AccountSetPassword.as_view()),
    url(r'^account/set_password_with_token/$', views.AccountSetPasswordWithToken.as_view()),
    url(r'^account/send_set_password_email/$', views.AccountSendSetPasswordEmail.as_view()),
    url(r'^account/me/$', views.AccountMe.as_view()),

    # other protected endpoints
    url(r'^files/upload_url/$', views.GetPresignedUploadUrl.as_view()),
]
