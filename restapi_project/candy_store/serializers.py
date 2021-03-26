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
        #fields = ['courier_id', 'courier_type', 'regions', 'working_hours', 'capacity']
        fields = '__all__'

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
        fields = ['order_id', 'weight', 'region', 'delivery_hours', 'courier']
        depth = 1

    def create(self, validated_data):
        delivery_hours_data = validated_data.pop('delivery_hours')
        order_item = OrderItem.objects.create(**validated_data)
        for hours in delivery_hours_data:
            order_item.delivery_hours.create(**hours)

        return order_item


class OrdersAssignSerializer(serializers.ModelSerializer):
    #courier = CourierItemSerializer(many=True)

    class Meta:
        model = OrderItem
        fields = ['courier']
        depth = 1
    '''
        for hours in couriers_data.data[idx_of_courier]['working_hours']:
            hour_begin, hour_end = int(hours['value'][:2]), int(hours['value'][6:8])
            minute_begin, minute_end = int(hours['value'][3:5]), int(hours['value'][9:11])
            for orders_idx in order_data.data: # by the objects
                for order_time in orders_idx['delivery_hours']: # by the time of object
                    order_hour = [int(order_time['value'][:2]), int(order_time['value'][6:8])]
                    order_minute = [int(order_time['value'][3:5]), int(order_time['value'][9:11])]
        '''
    '''
    def create(self, validated_data):
        # couriers_data = CourierItemSerializer(CourierItem.objects.all(), many=True)
        # order_data = OrderItemSerializer(OrderItem.objects.all(), many=True)

        print(validated_data)
        courier = CourierItem.objects.filter(courier_id=validated_data['courier_id'])
        if len(courier) > 0:
            orders_data = OrderItem.objects.all().values()
            for order in orders_data:
                if order['weight'] <= courier[0].capacity:
                    order['courier_id'] = courier[0]
                    order.save()
        # Looking the right time
    '''