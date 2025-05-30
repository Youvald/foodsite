# payment/models.py

from django.db import models

class Network(models.Model):
    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CryptoWallet(models.Model):
    CRYPTO_CHOICES = [
        ('USDT', 'USDT'),
        ('USDC', 'USDC'),
        ('ETH', 'ETH'),
        ('BNB', 'BNB'),
        ('LTC', 'LTC'),
    ]

    crypto = models.CharField(max_length=10, choices=CRYPTO_CHOICES)
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    contract_address = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('crypto', 'network')

    def __str__(self):
        return f"{self.crypto} ({self.network.name})"
