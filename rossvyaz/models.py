from django.db import models
from postgres_copy import CopyManager


class Operator(models.Model):
    name = models.CharField(max_length=200, unique=True)
    objects = CopyManager()


class Region(models.Model):
    name = models.CharField(max_length=200, unique=True)
    objects = CopyManager()


class Phone(models.Model):
    begin = models.BigIntegerField(db_index=True)
    end = models.BigIntegerField(db_index=True)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    objects = CopyManager()

    def __str__(self):
        return f'{self.begin}-{self.end}'

    @staticmethod
    def find(num):
        return Phone.objects.filter(begin__lte=num, end__gte=num).select_related().first()
