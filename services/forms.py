from django import forms
from .models import Service, Category


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'category', 'description', 'price', 'price_type',
                  'city', 'state', 'address', 'phone', 'email', 'image', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Service title'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0.00'}),
            'price_type': forms.Select(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'state': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
        }
