from django import forms
from accounts.models import DeliveryAddress


class CheckoutForm(forms.Form):
    name = forms.CharField(label="Ім’я", max_length=100)
    phone = forms.CharField(label="Номер телефону", max_length=13)

    DELIVERY_CHOICES = [
        ('delivery', 'Доставка'),
        ('pickup', 'Самовивіз'),
    ]
    delivery_type = forms.ChoiceField(choices=DELIVERY_CHOICES, label="Спосіб доставки")

    use_saved_address = forms.ModelChoiceField(
        queryset=DeliveryAddress.objects.none(),
        required=False,
        label="Виберіть збережену адресу"
    )

    street = forms.CharField(required=False, label="Вулиця")
    building = forms.CharField(required=False, label="Будинок")
    apartment = forms.CharField(required=False, label="Квартира",
                                widget=forms.TextInput(attrs={'placeholder': 'необов’язково'}))

    PAYMENT_CHOICES = [
        ('binance', 'Binance Pay'),
        ('liqpay', 'LiqPay'),
        ('cash', 'Готівкою при отриманні'),
    ]
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES, label="Спосіб оплати")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['use_saved_address'].queryset = DeliveryAddress.objects.filter(user=user)
