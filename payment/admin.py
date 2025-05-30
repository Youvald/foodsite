# payment/admin.py

from django.contrib import admin
from .models import CryptoWallet

@admin.register(CryptoWallet)
class CryptoWalletAdmin(admin.ModelAdmin):
    list_display = ('crypto', 'get_network_name', 'get_network_address')

    def get_network_name(self, obj):
        return obj.network.name
    get_network_name.short_description = 'Network'

    def get_network_address(self, obj):
        return obj.network.address
    get_network_address.short_description = 'Address'
