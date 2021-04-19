from django.db import models


class User(models.Model):
    email            = models.EmailField(max_length=255, unique=True)
    password         = models.CharField(max_length=200)
    corporation_name = models.CharField(max_length=200)
    is_verified      = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'
