REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler',
    # allow client to override using `?page_size={num}` in query string
    'DEFAULT_PAGINATION_CLASS': 'api.paginators.NoCountPagination',
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'api.throttles.BurstRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        # applies to all authenticated users, including w/ token auth, except admins
        'burst': '75/min',
        'authentication': '4/min',  # for users submitting username/email/password tuples to obtain token
    },
}

# This setting is IMPORTANT: without it, rest_framework.reverse.reverse, can't
# correct protocol/scheme for absolute URLs it generates. If the server receives
# requests via load balancer, make sure the balancer forwards the protocol
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
