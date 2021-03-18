from rest_framework import serializers

from .models import CourierItem


class CourierItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourierItem
        fields = ['courier_id', 'courier_type']
