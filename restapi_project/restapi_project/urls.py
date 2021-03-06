"""restapi_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from candy_store import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('couriers', views.CourierItemView.as_view()),
    path('orders', views.OrderItemView.as_view()),
    path('orders/assign', views.OrdersAssignView.as_view()),
    path('orders/complete', views.OrderCompleteView.as_view()),
    path('couriers/<int:c_id>', views.CourierAPView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
