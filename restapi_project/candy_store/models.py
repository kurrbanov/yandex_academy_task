from django.db import models
from django.core.validators import MaxValueValidator


class Region(models.Model):
    value = models.IntegerField(blank=False)


class WorkingHours(models.Model):
    value = models.CharField(blank=False, max_length=15)


class CourierItem(models.Model):
    courier_id = models.IntegerField(blank=False, unique=True)
    courier_type = models.CharField(max_length=4, blank=False)
    regions = models.ManyToManyField(Region, related_name='regions', blank=False)
    working_hours = models.ManyToManyField(WorkingHours, related_name='working_hours',
                                           blank=False)
    capacity = models.IntegerField(default=None)
    assign_time = models.DateTimeField(default=None, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    earnings = models.IntegerField(default=0)
    count_of_delivery = models.IntegerField(default=0)


class DeliveryHours(models.Model):
    value = models.CharField(max_length=15, blank=False)


class OrderItem(models.Model):
    order_id = models.IntegerField(blank=False, unique=True)
    weight = models.DecimalField(max_digits=4, decimal_places=2, blank=False,
                                 validators=[MaxValueValidator(50)])
    region = models.IntegerField(blank=False)
    delivery_hours = models.ManyToManyField(DeliveryHours, related_name='delivery_hours')
    courier = models.ForeignKey(CourierItem, on_delete=models.SET_NULL,
                                default=None, null=True)
    done = models.BooleanField(default=False)
    complete_time = models.DateTimeField(default=None, null=True)
    counted = models.BooleanField(default=False)
    type_of_courier_assign = models.CharField(default="", max_length=5)
    cnt_of_delivery = models.IntegerField(default=0)
