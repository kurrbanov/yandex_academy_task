import datetime

from rest_framework import status

from .models import CourierItem, OrderItem
from .serializers import CourierItemSerializer, OrderItemSerializer, OrdersAssignSerializer
from rest_framework.views import APIView
from rest_framework.response import Response


class CourierItemView(APIView):
    serializer_class = CourierItemSerializer

    def get(self, request, *args, **kwargs):
        couriers = CourierItem.objects.all()
        serializer = CourierItemSerializer(couriers, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        courier_data = request.data
        bad_idx = []
        good_idx = []

        for json_obj in courier_data['data']:
            change_list_json = json_obj['regions']
            json_obj['regions'] = [{"value": val} for val in change_list_json]
            change_list_json = json_obj['working_hours']
            json_obj['working_hours'] = [{"value": val} for val in change_list_json]
            change_list_json.clear()

            new_courier = CourierItemSerializer(data=json_obj)
            if new_courier.is_valid():
                new_courier.save()
                good_idx.append({"id": new_courier.data['courier_id']})
            else:
                bad_idx.append({"id": new_courier.data['courier_id']})

        if len(bad_idx) > 0:
            good_idx.clear()
            return Response({"validation_error": {"couriers": bad_idx}},
                            status=status.HTTP_400_BAD_REQUEST)

        bad_idx.clear()
        return Response({"couriers": good_idx}, status=status.HTTP_201_CREATED)


class OrderItemView(APIView):
    serializer_class = OrderItemSerializer

    def get(self, request, *args, **kwargs):
        orders = OrderItem.objects.all()
        serializer = OrderItemSerializer(orders, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        order_data = request.data
        bad_idx = []
        good_idx = []

        for json_obj in order_data['data']:
            change_list_json = json_obj['delivery_hours']
            json_obj['delivery_hours'] = [{"value": val} for val in change_list_json]
            change_list_json.clear()

            new_order_item = OrderItemSerializer(data=json_obj)
            if new_order_item.is_valid():
                new_order_item.save()
                good_idx.append({"id": new_order_item.data['order_id']})
            else:
                bad_idx.append({"id": new_order_item.data['order_id']})
                # return Response(new_order_item.errors)
            print(new_order_item.data)
        if len(bad_idx) > 0:
            good_idx.clear()
            return Response({"validation_error": {"orders": bad_idx}},
                            status=status.HTTP_400_BAD_REQUEST)

        bad_idx.clear()
        return Response({"orders": good_idx}, status=status.HTTP_201_CREATED)


class OrdersAssignView(APIView):
    serializer = OrderItemSerializer

    def get(self, request, *args, **kwargs):
        order = OrderItem.objects.all()
        serializer = OrdersAssignSerializer(order, many=True)

        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        orders_data = OrderItem.objects.all()

        courier_item = CourierItem.objects.filter(courier_id=request.data['courier'])

        if len(courier_item) == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        def check_region(val, query_set):
            for obj in query_set:
                if val == obj.value:
                    return True
            return False

        def paint_time_line(time_line, minutes_line, hours, color):
            for obj in hours:
                hours_begin, hours_end = int(obj.value[:2]), int(obj.value[6:8])
                min_begin, min_end = int(obj.value[3:5]), int(obj.value[9:11])

                if min_end == 0:
                    hours_end -= 1
                    min_end = 59

                for h in range(hours_begin, hours_end + 1):
                    if time_line[h] == 0:
                        time_line[h] = color
                    if h == hours_begin:
                        for m in range(min_begin, 60):
                            if minutes_line[h][m] == 0:
                                minutes_line[h][m] = color
                            else:
                                return True
                    elif h == hours_end:
                        for m in range(0, min_end + 1):
                            minutes_line[h][m] = color
                    else:
                        for m in range(0, 60):
                            if minutes_line[h][m] == 0:
                                minutes_line[h][m] = color
                            else:
                                return True
                return False

        def check_hours(hours_order, hours_courier):
            time_line = [0 for i in range(24)]
            minutes_line = [[0 for i in range(60)] for j in range(24)]

            # покраска временной линии курьера
            paint_time_line(time_line, minutes_line, hours_courier, 1)

            # покраска временной линии продукта
            return paint_time_line(time_line, minutes_line, hours_order, 2)

        courier_item = courier_item[0]
        count_assign_orders = 0

        for order in orders_data:
            if not(order.courier is None):
                continue

            if order.weight <= courier_item.capacity and \
                    check_region(order.region, courier_item.regions.all()) and \
                    check_hours(order.delivery_hours.all(), courier_item.working_hours.all()):
                order.courier = courier_item
                order.save()
                count_assign_orders += 1

        d = datetime.datetime.utcnow().isoformat("T") + "Z"
        ans = []
        for item in courier_item.orderitem_set.all():
            if not item.done:
                ans.append({"id": item.order_id})

        if count_assign_orders > 0:
            courier_item.assign_time = d
            return Response({"orders": ans, "assign_time": d}, status=status.HTTP_200_OK)

        if len(ans) > 0:
            return Response({"orders": ans, "assign_time": courier_item.assign_time},
                            status=status.HTTP_200_OK)

        return Response({"orders": ans}, status=status.HTTP_200_OK)
