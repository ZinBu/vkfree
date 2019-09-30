import uuid
from datetime import datetime

from django.db import models


class User(models.Model):
    first_name = models.CharField(max_length=200, default='')
    last_name = models.CharField(max_length=200, default='')
    uid = models.CharField(max_length=200, default='')
    extra_token = models.CharField(max_length=200, default='')
    photo = models.CharField(max_length=300, default='')

    def __str__(self):
        return self.fullname

    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name}"

    def get_token(self, token):
        return self.extra_token or token


class Session(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=200, default='')
    token = models.CharField(max_length=200, default='')
    created = models.DateTimeField(default=datetime.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user_id


class Task(models.Model):
    user_id = models.CharField(max_length=200, default='')
    busy = models.BooleanField(default=False)
    updated = models.DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        super().save(*args, **kwargs)
