from django.db import models
from django.conf import settings
from menu.models import Dish
from django.contrib.auth import get_user_model
from accounts.models import CustomUser
from payment.models import CryptoWallet


User = get_user_model()

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='order_addresses')
    city = models.CharField(max_length=100, default='Івано-Франківськ')
    street = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.city}, {self.street}"


class Order(models.Model):
    DELIVERY_CHOICES = [
        ('delivery', 'Доставка'),
        ('pickup', 'Самовивіз'),
        ('reserve_ready', 'Бронювання зі стравами'),
        ('reserve_only', 'Бронювання без страв'),
    ]

    PAYMENT_CHOICES = [
        ('crypto', 'Криптовалюта'),
        ('cash', 'Готівкою при отриманні'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Очікує'),
        ('paid', 'Оплачено'),
        ('in_process', 'Готується'),
        ('done', 'Виконано'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True, null=True)
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    crypto_wallet = models.ForeignKey(CryptoWallet, on_delete=models.SET_NULL, null=True, blank=True)
    crypto_amount = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)

    def __str__(self):
        return f"Замовлення #{self.id} — {self.created_at.date()}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.dish.name}"
    def total_price(self):
        return self.quantity * self.price
