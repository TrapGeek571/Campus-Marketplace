# lostfound/forms.py
from django import forms
from .models import LostItem

class LostItemForm(forms.ModelForm):
    class Meta:
        model = LostItem
        fields = ['item_type', 'item_name', 'description', 'location', 'date_lost', 'status', 'image', 'contact_info']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the item...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Where was it lost/found?'}),
            'date_lost': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your contact information'}),
            'item_type': forms.Select(attrs={'class': 'form-control'}),
        }