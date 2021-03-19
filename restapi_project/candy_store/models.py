from django.db import models


class Region(models.Model):
    value = models.IntegerField(blank=False)


class WorkingHours(models.Model):
    value = models.CharField(blank=False, max_length=15)


class CourierItem(models.Model):
    courier_id = models.IntegerField(blank=False, unique=True)
    courier_type = models.CharField(max_length=4, blank=False)  # добавить выбор
    region = models.ManyToManyField(Region, related_name='region',
                                    blank=False)
    working_hours = models.ManyToManyField(WorkingHours, related_name='working_hours',
                                           blank=False)
    capacity = models.IntegerField(default=None)
