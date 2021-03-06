from __future__ import unicode_literals

from django.contrib.auth.models import Permission, User
from django.db import models

# Create your models here.
class Video(models.Model):
    user = models.ForeignKey(User, default=1)
    title = models.CharField(max_length=30)
    videofile = models.FileField()
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title + '-' + self.user

class Comment(models.Model):
    user = models.ForeignKey(User, default=1)
    video = models.ForeignKey(Video, default=1)
    comment = models.TextField(max_length=100)


class Search(models.Model):
    type = models.CharField(max_length=6)
    time = models.FloatField(max_length=None)











































