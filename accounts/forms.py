from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser
from .models import DeliveryAddress
import re

class AddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = ['city', 'street', 'building', 'apartment', 'is_default']
        labels = {
            'city': 'Місто',
            'street': 'Вулиця',
            'building': 'Будинок',
            'apartment': 'Квартира',
            'is_default': 'Основна адреса',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].initial = 'Івано-Франківськ'
        self.fields['city'].widget.attrs['readonly'] = True

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Підтвердження пароля", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'phone']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match(r'^\+380\d{9}$', phone):
            raise forms.ValidationError("Номер телефону має бути у форматі +380XXXXXXXXX")
        return phone

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

