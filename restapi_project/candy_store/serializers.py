from .models import CourierItem
from rest_framework import serializers


class CourierItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CourierItem
        fields = ['courier_id', 'courier_type']

