# lostfound/forms.py
from django import forms
from django.utils import timezone
import datetime
from .models import LostFoundItem

class LostFoundItemForm(forms.ModelForm):
    # Using HTML5 date input - simple and reliable
    date_lost = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'max': timezone.now().date().isoformat(),
                'min': (timezone.now().date() - datetime.timedelta(days=365)).isoformat(),
            }
        ),
        help_text="Select a date between one year ago and today"
    )
    
    class Meta:
        model = LostFoundItem
        fields = ['category', 'item_name', 'description', 'location', 'contact_info', 'date_lost', 'status', 'image']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., iPhone, Wallet, Keys'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the item...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Where was it lost/found?'}),
            'contact_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Your contact info'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        
        # CloudinaryField doesn't need special widget, Django handles it
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial date to today if creating new
        if not self.instance.pk:
            self.fields['date_lost'].initial = timezone.now().date()
    
    def clean_date_lost(self):
        date_lost = self.cleaned_data.get('date_lost')
        today = timezone.now().date()
        one_year_ago = today - datetime.timedelta(days=365)
        
        if date_lost > today:
            raise forms.ValidationError("Date cannot be in the future!")
        if date_lost < one_year_ago:
            raise forms.ValidationError("Date cannot be more than one year in the past!")
        
        return date_lost

class LostFoundItemSearchForm(forms.Form):
    """Form for searching lost/found items"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search items...'
        })
    )
    category = forms.ChoiceField(
        required=False,
        choices=[('', 'All Categories')] + LostFoundItem.CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + LostFoundItem.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )