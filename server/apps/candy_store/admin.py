from django.contrib import admin
from .models import CourierItem, OrderItem

admin.site.register(CourierItem)
admin.site.register(OrderItem)
