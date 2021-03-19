from rest_framework import serializers

from .models import CourierItem, Region, WorkingHours, OrderItem, DeliveryHours


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['value']


class WorkingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHours
        fields = ['value']


class CourierItemSerializer(serializers.ModelSerializer):
    regions = RegionSerializer(many=True)
    working_hours = WorkingHoursSerializer(many=True)

    class Meta:
        model = CourierItem
        fields = ['courier_id', 'courier_type', 'regions', 'working_hours']

    def create(self, validated_data):
        region_data = validated_data.pop('regions')
        working_hours_data = validated_data.pop('working_hours')

        if validated_data['courier_type'] == 'foot':
            validated_data['capacity'] = 10
        elif validated_data['courier_type'] == 'bike':
            validated_data['capacity'] = 15
        elif validated_data['courier_type'] == 'car':
            validated_data['capacity'] = 50

        courier_item = CourierItem.objects.create(**validated_data)
        for reg in region_data:
            courier_item.regions.create(**reg)
        for work in working_hours_data:
            courier_item.working_hours.create(**work)

        return courier_item


class DeliveryHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryHours
        fields = ['value']


class OrderItemSerializer(serializers.ModelSerializer):
    delivery_hours = DeliveryHoursSerializer(many=True)

    class Meta:
        model = OrderItem
        fields = ['order_id', 'weight', 'region', 'delivery_hours']

    def create(self, validated_data):
        delivery_hours_data = validated_data.pop('delivery_hours')
        order_item = OrderItem.objects.create(**validated_data)
        for hours in delivery_hours_data:
            order_item.delivery_hours.create(**hours)

        return order_item
