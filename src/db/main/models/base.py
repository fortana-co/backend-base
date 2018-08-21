from django.contrib.gis.db import models

from db.config import BaseModel
from db.choices import APP_TYPE_CHOICES


class AppVersion(BaseModel):
    app_type = models.TextField(choices=APP_TYPE_CHOICES, db_index=True)
    git_hash = models.TextField(db_index=True)

    @property
    def git_hash_short(self):
        return self.git_hash[:7]

    class Meta:
        ordering = ('-created',)
