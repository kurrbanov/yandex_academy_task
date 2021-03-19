from rest_framework import status

from .models import CourierItem, OrderItem
from .serializers import CourierItemSerializer, OrderItemSerializer
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
            return Response({"validation_error": {"couriers": bad_idx}}, status=status.HTTP_400_BAD_REQUEST)

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
        ival = request.META.get('HTTP_X_IDEMPOTENCY_KEY')

        print(ival)
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

        if len(bad_idx) > 0:
            good_idx.clear()
            return Response({"validation_error": {"orders": bad_idx}},
                            status=status.HTTP_400_BAD_REQUEST)

        bad_idx.clear()
        return Response({"orders": good_idx}, status=status.HTTP_201_CREATED)
