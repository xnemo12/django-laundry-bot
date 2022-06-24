from django.db import models

from utils.models import CreateUpdateTracker, nb


class ProductCategory(CreateUpdateTracker):
    name = models.CharField(max_length=200, **nb)
    lang = models.CharField(max_length=8, **nb)
    emoji = models.CharField(max_length=5, **nb)
    order = models.IntegerField(**nb)

    def __str__(self):
        return self.name


class Product(CreateUpdateTracker):
    name = models.CharField(max_length=255, **nb)
    lang = models.CharField(max_length=8, **nb)
    price = models.FloatField(**nb)
    uom = models.CharField(max_length=30, **nb)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=5, **nb)
    order = models.IntegerField(**nb)

    def __str__(self):
        return self.name
