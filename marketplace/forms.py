# marketplace/forms.py
from django import forms
from .models import Product, Category
from datetime import date, timedelta

class ProductForm(forms.ModelForm):
    def clean_created_at(self):
        created_at = self.cleaned_data.get('created_at')
        if created_at:
            today = date.today()
            if created_at > today:
                raise forms.ValidationError("Date cannot be in the future.")
        return created_at
    
    class Meta:
        model = Product
        fields = ['title', 'description', 'category', 'price', 'condition', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your product...'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price in KSH', 'min':'0', 'step':'0.1'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
        }