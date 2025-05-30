from django import forms
from payment.models import Network, CryptoWallet


class CryptoPaymentForm(forms.Form):
    crypto = forms.ChoiceField(
        choices=[('', '---------')] + CryptoWallet.CRYPTO_CHOICES,
        label="Crypto",
        required=True
    )
    network = forms.ModelChoiceField(
        queryset=Network.objects.none(),
        label="Network",
        required=True,
        empty_label="---------"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'crypto' in self.data:
            crypto = self.data.get('crypto')
            self.fields['network'].queryset = Network.objects.filter(cryptowallet__crypto=crypto).distinct()
        else:
            self.fields['network'].queryset = Network.objects.none()
