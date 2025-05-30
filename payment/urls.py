from django.urls import path
from .views import select_crypto_payment, crypto_payment_page, payment_success, get_networks_for_crypto, check_payment_status

urlpatterns = [
    path('order/<int:order_id>/select/', select_crypto_payment, name='select_crypto_payment'),  # ✅ з order_id
    path('order/<int:order_id>/payment/', crypto_payment_page, name='crypto_payment_page'),
    path('success/<int:order_id>/', payment_success, name='payment_success'),
    path('ajax/get-networks/', get_networks_for_crypto, name='get_networks_for_crypto'),
    path('order/<int:order_id>/check/', check_payment_status, name='check_payment_status'),
]
