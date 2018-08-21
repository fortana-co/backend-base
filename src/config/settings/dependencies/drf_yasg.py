SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        },
    },
    'DEFAULT_AUTO_SCHEMA_CLASS': 'api.openapi.CustomAutoSchema',
}
