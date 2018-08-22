from __future__ import absolute_import

from datetime import timedelta


CELERY_IMPORTS = (
)

CELERY_ENABLE_UTC = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERYD_TASK_SOFT_TIME_LIMIT = 90

CELERYBEAT_SCHEDULE = {
}
