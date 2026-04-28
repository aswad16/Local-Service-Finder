from django import forms
from services.models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'icon', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Category name'}),
            'icon': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Emoji icon e.g. 🔧'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }
