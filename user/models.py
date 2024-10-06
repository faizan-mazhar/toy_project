from django.db import models
from django.contrib.auth.models import AbstractUser


class Writer(AbstractUser):
    name = models.CharField(max_length=100)
    is_editor = models.BooleanField(default=False)
