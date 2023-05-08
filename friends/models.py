from django.db import models


class User(models.Model):

    ID = models.AutoField(primary_key=True)
    Username = models.CharField(max_length=30, unique=True)
    TrueName = models.CharField(max_length=40)

    def __str__(self):
        return self.Username
