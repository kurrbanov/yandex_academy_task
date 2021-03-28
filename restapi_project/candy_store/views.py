import datetime
import dateutil.parser

from rest_framework import status

from .models import CourierItem, OrderItem, Region, WorkingHours
from .serializers import CourierItemSerializer, OrderItemSerializer, OrdersAssignSerializer, \
    OrderCompleteSerializer, CourierAPSerializer, CourierItemAPSerializer
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

            def check_type(tpe):
                if tpe == 'foot' or tpe == 'car' or tpe == 'bike':
                    return True

            new_courier = CourierItemSerializer(data=json_obj)
            if new_courier.is_valid() and len(json_obj['regions']) > 0 and \
                    len(json_obj['working_hours']) > 0 and check_type(json_obj['courier_type']):
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

            if len(json_obj['delivery_hours']) == 0:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            new_order_item = OrderItemSerializer(data=json_obj)
            if new_order_item.is_valid():
                new_order_item.save()
                good_idx.append({"id": new_order_item.data['order_id']})
            else:
                bad_idx.append({"id": new_order_item.data['order_id']})
                # return Response(new_order_item.errors)
        if len(bad_idx) > 0:
            good_idx.clear()
            return Response({"validation_error": {"orders": bad_idx}},
                            status=status.HTTP_400_BAD_REQUEST)

        bad_idx.clear()
        return Response({"orders": good_idx}, status=status.HTTP_201_CREATED)


class OrderAssignValidators:
    @staticmethod
    def check_region(val, query_set):
        for obj in query_set:
            if val == obj.value:
                return True
        return False

    @staticmethod
    def paint_time_line(minutes_line, hours, color):
        for obj in hours:
            hours_begin, hours_end = int(obj.value[:2]), int(obj.value[6:8])
            min_begin, min_end = int(obj.value[3:5]), int(obj.value[9:11])

            count_intersection = 0
            for h in range(hours_begin, hours_end + 1):
                if h == hours_begin:
                    for m in range(min_begin, 60):
                        if minutes_line[h][m] == 0:
                            minutes_line[h][m] = color
                        else:
                            count_intersection += 1
                elif h == hours_end:
                    for m in range(0, min_end + 1):
                        if minutes_line[h][m] == 0:
                            minutes_line[h][m] = color
                        else:
                            count_intersection += 1
                else:
                    for m in range(0, 60):
                        if minutes_line[h][m] == 0:
                            minutes_line[h][m] = color
                        else:
                            count_intersection += 1
                if count_intersection >= 2:
                    return True

            return False

    @staticmethod
    def check_hours(hours_order, hours_courier):
        minutes_line = [[0 for i in range(60)] for j in range(24)]

        # покраска временной линии курьера
        OrderAssignValidators.paint_time_line(minutes_line, hours_courier, 1)

        # покраска временной линии продукта
        return OrderAssignValidators.paint_time_line(minutes_line, hours_order, 2)


class OrdersAssignView(APIView):
    serializer = OrderItemSerializer

    def get(self, request, *args, **kwargs):
        order = OrderItem.objects.all()
        serializer = OrdersAssignSerializer(order, many=True)

        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        orders_data = OrderItem.objects.all()

        courier_item = CourierItem.objects.filter(courier_id=request.data['courier_id'])

        if len(courier_item) == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        courier_item = courier_item[0]
        count_assign_orders = 0

        for order in orders_data:
            if not(order.courier is None) and order.done:
                continue

            if order.weight <= courier_item.capacity and \
                    OrderAssignValidators.check_region(order.region, courier_item.regions.all()) and \
                    OrderAssignValidators.check_hours(order.delivery_hours.all(),
                                                      courier_item.working_hours.all()):
                order.courier = courier_item
                order.save()
                count_assign_orders += 1

        ans = []
        for item in courier_item.orderitem_set.all():
            if not item.done:
                ans.append({"id": item.order_id})

        if count_assign_orders > 0:
            courier_item.assign_time = datetime.datetime.utcnow()
            courier_item.save()

        if len(ans) > 0:
            return Response({"orders": ans, "assign_time": courier_item.assign_time.isoformat("T") + "Z"},
                            status=status.HTTP_200_OK)

        return Response({"orders": ans}, status=status.HTTP_200_OK)


class OrderCompleteView(APIView):
    def get(self, request, *args, **kwargs):
        order = OrderItem.objects.all()
        serializer = OrderCompleteSerializer(order, many=True)

        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        courier = CourierItem.objects.filter(courier_id=request.data['courier_id'])

        if len(courier) == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        courier = courier[0]
        for orders in courier.orderitem_set.all():
            if orders.order_id == request.data['order_id']:
                orders.done = True
                orders.complete_time = dateutil.parser.isoparse(request.data['complete_time'])
                orders.save()
                return Response({"order_id": orders.order_id}, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class CourierAPView(APIView):
    def patch(self, request, c_id):
        courier_data = CourierItem.objects.filter(courier_id=c_id)

        if len(courier_data) == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        courier = courier_data[0]

        def check_type(tpe):
            if tpe == 'foot':
                return [True, 10]
            if tpe == 'car':
                return [True, 50]
            if tpe == 'bike':
                return [True, 15]
            return [False, -1]

        for json_data in request.data:
            if json_data == "courier_type":
                if check_type(request.data[json_data])[0]:
                    courier.courier_type = request.data[json_data]
                    courier.capacity = check_type(request.data[json_data])[1]
                    courier.save()
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            elif json_data == "regions":
                courier.regions.clear()
                for regions in request.data[json_data]:
                    r = Region.objects.create(value=regions)
                    r.save()
                    courier.regions.add(r)
                courier.save()
            elif json_data == 'working_hours':
                courier.working_hours.clear()
                for hours in request.data[json_data]:
                    wh = WorkingHours.objects.create(value=hours)
                    courier.working_hours.add(wh)
                courier.save()
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        # обновление списка заказов
        orders = courier.orderitem_set.all()
        for order in orders:
            if not(OrderAssignValidators.check_region(order.region, courier.regions.all()) and
                   OrderAssignValidators.check_hours(order.delivery_hours.all(), courier.working_hours.all()) and
                   order.weight <= courier.capacity) and not order.done:
                order.courier = None
                order.complete_time = ""
                order.save()

        courier_serializer = CourierItemAPSerializer(CourierItem.objects.all(), many=True)
        return Response(courier_serializer.data, status=status.HTTP_200_OK)

    def get(self, request, c_id):
        # подсчёт рейтинга
        courier = CourierItem.objects.filter(courier_id=c_id)
        if len(courier) == 0:
            return Response({"Error": "Courier doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)

        courier = courier[0]
        orders = courier.orderitem_set.all()

        td = {
            # region: [time_sum_sec, количество выполненных заказов из данного региона]
        }
        count_done_orders = 0
        for order in orders:
            if order.done and not order.counted:
                count_done_orders += 1
                time_delivery = order.complete_time - courier.assign_time
                if order.region not in td:
                    td[order.region] = [time_delivery.seconds, 1]
                else:
                    new_time = td[order.region][0] + time_delivery.seconds
                    cnt = td[order.region][1] + 1
                    td[order.region] = [new_time, cnt]
                order.counted = True
                order.save()

        t = -1
        for region in td:
            average_time_by_region = td[region][0] / td[region][1]
            if t == -1:
                t = average_time_by_region
                continue
            t = min(t, average_time_by_region)

        if count_done_orders > 0:
            # courier.rating = round((float(courier.rating) + round((60 * 60 - min(t, 60 * 60))/(60 * 60) * 5, 2)) / 2, 2)
            courier.rating = round((60 * 60 - min(t, 60 * 60))/(60 * 60) * 5, 2)
            courier.save()

            # подсчёт заработка
            if courier.courier_type == 'foot':
                courier.earnings += count_done_orders * 1000
            elif courier.courier_type == 'bike':
                courier.earnings += count_done_orders * 2500
            elif courier.courier_type == 'car':
                courier.earnings += count_done_orders * 4500
            courier.save()

        courier_serializer = CourierAPSerializer(CourierItem.objects.all(), many=True)
        return Response(courier_serializer.data, status=status.HTTP_200_OK)