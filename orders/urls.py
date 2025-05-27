from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('orders/', views.user_orders_view, name='order_list'),

]
