from django.db import models


class Operator(models.Model):
    name = models.CharField(max_length=200, unique=True)


class Region(models.Model):
    name = models.CharField(max_length=200, unique=True)


class Phone(models.Model):
    begin = models.BigIntegerField(db_index=True)
    end = models.BigIntegerField(db_index=True)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.begin}-{self.end}'
