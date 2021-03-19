from rest_framework import serializers

from .models import CourierItem, Region, WorkingHours


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['value']


class WorkingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHours
        fields = ['value']


class CourierItemSerializer(serializers.ModelSerializer):
    region = RegionSerializer(many=True)
    working_hours = WorkingHoursSerializer(many=True)

    class Meta:
        model = CourierItem
        fields = ['courier_id', 'courier_type', 'region', 'working_hours']

    def create(self, validated_data):
        region_data = validated_data.pop('region')
        working_hours_data = validated_data.pop('working_hours')

        if validated_data['courier_type'] == 'foot':
            validated_data['capacity'] = 10
        elif validated_data['courier_type'] == 'bike':
            validated_data['capacity'] = 15
        elif validated_data['courier_type'] == 'car':
            validated_data['capacity'] = 50

        courier_item = CourierItem.objects.create(**validated_data)
        for reg in region_data:
            courier_item.region.create(**reg)
        for work in working_hours_data:
            courier_item.working_hours.create(**work)

        return courier_item
