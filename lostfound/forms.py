# lostfound/forms.py
from django import forms
from django.utils import timezone
import datetime
from datetime import timedelta
from .models import LostFoundItem

class LostFoundItemForm(forms.ModelForm):
    date_lost = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'dd/mm/yyyy',
                'autocomplete': 'off',
                'id': 'date-lost-input',
            }
        ),
        input_formats=['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'],
        help_text="Format: DD/MM/YYYY",
    )
    
    class Meta:
        model = LostFoundItem
        fields = ['category', 'item_name', 'description', 'location', 'date_lost', 'status', 'image', 'contact_info']
        
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'item_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., iPhone 12, Calculus Textbook',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the item (color, brand, distinguishing features, etc.)',
                'required': 'required'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Main Library, Room 205',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'contact_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Your phone number, email, or other contact info',
                'required': 'required'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial date format for display
        if self.instance and self.instance.date_lost:
            self.initial['date_lost'] = self.instance.date_lost.strftime('%d/%m/%Y')
        
        # Add 'required' attribute to all fields except image
        for field_name, field in self.fields.items():
            if field_name != 'image':
                field.widget.attrs['required'] = 'required'
    
    def clean_date_lost(self):
        date_lost = self.cleaned_data.get('date_lost')
        if not date_lost:
            raise forms.ValidationError("This field is required.")
        
        today = timezone.now().date()
        one_year_ago = today - datetime.timedelta(days=365)
        
        if date_lost > today:
            raise forms.ValidationError("Date cannot be in the future!")
        if date_lost < one_year_ago:
            raise forms.ValidationError("Date cannot be more than one year in the past!")
        
        return date_lost
    
    def clean(self):
        cleaned_data = super().clean()
        # Add any cross-field validation here
        return cleaned_data