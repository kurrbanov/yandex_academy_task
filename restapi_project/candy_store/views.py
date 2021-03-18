from rest_framework import status

from .models import CourierItem
from .serializers import CourierItemSerializer
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
        print(f"courier_data: {courier_data}")
        print(f"{courier_data['data'][0]}")
        print()
        bad_idx = []
        good_idx = []

        for json_obj in courier_data['data']:
            new_courier = CourierItemSerializer(data=json_obj)
            if new_courier.is_valid():
                new_courier.save()
                good_idx.append({"id": new_courier.data['courier_id']})
            else:
                bad_idx.append({"id": new_courier.data['courier_id']})

        if len(bad_idx) > 0:
            return Response({"couriers": bad_idx}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"couriers": good_idx}, status=status.HTTP_201_CREATED)

'''
        new_courier = CourierItem.objects.create(courier_id=courier_data['courier_id'],
                                                 courier_type=courier_data['courier_type'])

        new_courier.save()
        serializer = CourierItemSerializer(new_courier)

        print(f"new_courier: {new_courier}")
        print(f"serializer: {serializer}")
        print(f"serializer.data: {serializer.data}")

        return Response(serializer.data, status=status.HTTP_200_OK)
'''