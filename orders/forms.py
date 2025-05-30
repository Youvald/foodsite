from django import forms
from .models import Address
from payment.models import CryptoWallet, Network

class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=100, label='Ім’я')
    phone = forms.CharField(max_length=20, label='Телефон')
    delivery_type = forms.ChoiceField(choices=[
        ('delivery', 'Доставка'),
        ('pickup', 'Самовивіз'),
    ], label='Тип доставки')

    payment_method = forms.ChoiceField(choices=[
        ('crypto', 'Криптовалюта'),
        ('cash', 'Готівка при отриманні'),
    ], label='Спосіб оплати')

    use_saved_address = forms.ModelChoiceField(
        queryset=Address.objects.none(), required=False, label='Збережена адреса'
    )
    street = forms.CharField(max_length=255, required=False)
    building = forms.CharField(max_length=50, required=False)
    apartment = forms.CharField(max_length=20, required=False)

    crypto = forms.ChoiceField(
        choices=[('', '---------')] + CryptoWallet.CRYPTO_CHOICES, required=False, label='Криптовалюта'
    )
    network = forms.ModelChoiceField(
        queryset=Network.objects.none(), required=False, label='Мережа'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['use_saved_address'].queryset = Address.objects.filter(user=user)

        if 'crypto' in self.data:
            crypto = self.data.get('crypto')
            self.fields['network'].queryset = Network.objects.filter(cryptowallet__crypto=crypto).distinct()
        else:
            self.fields['network'].queryset = Network.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')

        if payment_method == 'crypto':
            if not cleaned_data.get('crypto'):
                self.add_error('crypto', 'Оберіть криптовалюту')
            if not cleaned_data.get('network'):
                self.add_error('network', 'Оберіть мережу')
