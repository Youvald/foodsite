from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('dish', 'quantity', 'price')
    can_delete = False

    def total_price(self, obj):
        return obj.total_price()
    total_price.short_description = 'Сума'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'phone', 'delivery_type', 'payment_method', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'delivery_type', 'payment_method')

    readonly_fields = (
        'user', 'first_name', 'phone', 'address',
        'delivery_type', 'payment_method', 'total_price', 'created_at'
    )

    fields = (
        'user', 'first_name', 'phone', 'address',
        'delivery_type', 'payment_method', 'total_price', 'created_at',
        'status'  # поле доступне для редагування
    )

    inlines = [OrderItemInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
