from django.db import models


class Tarifs(models.Model):
    """Модель тарифов"""

    article = models.IntegerField()
    title = models.CharField(max_length=100)
    parametrs = models.CharField(max_length=300)
    options = models.CharField(max_length=300)
    price = models.FloatField(null=True)
    price_old = models.FloatField(null=True)

    def __str__(self):
        return self.title
