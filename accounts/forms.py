from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Підтвердження пароля", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'phone']

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 != p2:
            raise forms.ValidationError("Паролі не співпадають")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Номер телефону")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

from .models import DeliveryAddress

class AddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = ['city', 'street', 'building', 'apartment', 'is_default']
