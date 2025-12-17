# housing/forms.py
from django import forms
from .models import Property

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'description', 'property_type', 'address', 'rent', 'bedrooms', 'bathrooms', 'is_furnished', 'image', 'available_from', 'contact_info', 'is_available']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Property Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the property...'}),
            'property_type': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Address'}),
            'rent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Monthly Rent in KSH'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact information'}),
        }