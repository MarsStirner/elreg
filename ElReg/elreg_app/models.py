# -*- coding: utf-8 -*-

from django.db import models
import config

class Region (models.Model):
    """Модель БД с названиями МО и их кодах ОКАТО
    Модель, описывающая поля в БД с названиями МО (region) и их кодах ОКАТО (code). Чтобы не удалять МО из
    таблицы введено поле activation, указывающее на доступность/недоступность данного МО шаблону сайта.

    """
    region = models.CharField(max_length=100,)
    code = models.BigIntegerField(default=0, max_length=12)
    activation = models.BooleanField(default=True)

    def __unicode__(self):
        return self.region

    class Meta:
        ordering = ('-activation', 'region')