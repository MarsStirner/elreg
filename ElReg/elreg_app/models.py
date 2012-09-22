from django.db import models

class Region (models.Model):
    region = models.CharField(max_length=100,)
    code = models.PositiveIntegerField(default=0)
    activation = models.BooleanField(default=True)

    def __unicode__(self):
        return self.region

    class Meta:
        ordering = ('-activation', 'region')