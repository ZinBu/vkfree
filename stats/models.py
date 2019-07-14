from datetime import datetime

from django.db import models


class User(models.Model):
    fullname = models.CharField(max_length=200, default='')
    uid = models.CharField(max_length=200, default='')
    nickname = models.CharField(max_length=200, default='')
    extra_token = models.CharField(max_length=200, default='')
    token_got = models.DateTimeField('date token got', default=datetime.now)

    def __str__(self):
        return self.fullname


class Task(models.Model):
    nickname = models.CharField(max_length=200, default='')
    busy = models.BooleanField(default=False)
    updated = models.DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        super().save(*args, **kwargs)
