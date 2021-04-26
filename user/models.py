from django.db import models


class User(models.Model):
    email            = models.EmailField(max_length=255, unique=True)
    password         = models.CharField(max_length=200)
    corporation_name = models.CharField(max_length=200)
    is_verified      = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'

class GridLayout(models.Model):
    id           = models.CharField(max_length=100, primary_key=True)
    x            = models.IntegerField()
    y            = models.IntegerField()
    w            = models.IntegerField()
    h            = models.IntegerField()
    is_draggable = models.BooleanField(default=True)
    user_id      = models.ForeignKey('User', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'grid_layouts'

