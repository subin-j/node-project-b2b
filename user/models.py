from django.db import models


class User(models.Model):
    email        = models.EmailField(max_length=254, unique=True)
    password     = models.CharField(max_length=254)
    corp         = models.CharField(max_length=50)
    is_verified  = model.models.BooleanField(default=False)

    class Meta:
        db_table = 'users'