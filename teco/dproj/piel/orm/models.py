from django.db import models

class Robot(models.Model):
    nombre =  models.CharField(max_length=30)
