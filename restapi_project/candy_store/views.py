# from django.shortcuts import render, HttpResponse
from rest_framework import viewsets
# from rest_framework.response import Response
from .serializers import CourierItemSerializer
from .models import CourierItem


class CourierItemView(viewsets.ModelViewSet):
    queryset = CourierItem.objects.all()
    serializer_class = CourierItemSerializer
