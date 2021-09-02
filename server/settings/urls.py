from django.contrib import admin
from django.urls import path, include
from apps.candy_store import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('couriers', views.CourierItemView.as_view()),
    path('orders', views.OrderItemView.as_view()),
    path('orders/assign', views.OrdersAssignView.as_view()),
    path('orders/complete', views.OrderCompleteView.as_view()),
    path('couriers/<int:c_id>', views.CourierAPView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
