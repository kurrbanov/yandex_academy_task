from django.db import models


class CourierItem(models.Model):
    courier_id = models.IntegerField(blank=False)
    courier_type = models.CharField(max_length=6, blank=False)
