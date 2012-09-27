#coding: utf-8
from django.db import models

class Region (models.Model):
    """
    Модель для хранения данных в БД о названии МО и его коде ОКАТО
    """
    region = models.CharField(max_length=100,)
    code = models.PositiveIntegerField(default=0)
    activation = models.BooleanField(default=True)

    def __unicode__(self):
        return self.region

    class Meta:
        ordering = ('-activation', 'region')