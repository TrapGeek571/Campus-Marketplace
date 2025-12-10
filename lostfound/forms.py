from django import forms
from .models import LostItem
from django.utils import timezone
import datetime

class LostItemForm(forms.ModelForm):
    # Explicitly define the item_type field to control choices
    item_type = forms.ChoiceField(
        choices=[('lost', 'Lost'), ('found', 'Found')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Is this a lost or found item? *',
        required=True,
        initial='lost',  # Set default to 'lost'
    )
    
    class Meta:
        model = LostItem
        fields = [
            'title', 'description', 'item_type', 'category',
            'location_lost', 'location_found', 'date_lost', 'date_found',
            'image', 'contact_email', 'contact_phone'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'date_lost': forms.DateInput(attrs={
                'type': 'date', 
                'max': datetime.date.today().isoformat(),
                'class': 'form-control'
            }),
            'date_found': forms.DateInput(attrs={
                'type': 'date', 
                'max': datetime.date.today().isoformat(),
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'location_lost': forms.TextInput(attrs={'class': 'form-control'}),
            'location_found': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = datetime.date.today()
        
        # Set max date for both date fields in HTML5
        self.fields['date_lost'].widget.attrs['max'] = today.isoformat()
        self.fields['date_found'].widget.attrs['max'] = today.isoformat()
        
        # Remove empty choice from category field if it exists
        if self.fields['category'].choices and self.fields['category'].choices[0] == ('', '---------'):
            self.fields['category'].choices = self.fields['category'].choices[1:]
    
    def clean_date_lost(self):
        """Validate that date_lost is not in the future and not too far in the past."""
        date_lost = self.cleaned_data.get('date_lost')
        if date_lost:
            today = datetime.date.today()
            one_year_ago = today - datetime.timedelta(days=365)
            if date_lost > today:
                raise forms.ValidationError('Date lost cannot be in the future!')
            if date_lost < one_year_ago:
                raise forms.ValidationError('Date lost cannot be more than 1 year ago!')    
        return date_lost
    
    def clean_date_found(self):
        """Validate that date_found is not in the future and not too far in the past."""
        date_found = self.cleaned_data.get('date_found')
        if date_found:
            today = datetime.date.today()
            one_year_ago = today - datetime.timedelta(days=365)
            if date_found > today:
                raise forms.ValidationError('Date found cannot be in the future!')
            if date_found < one_year_ago:
                raise forms.ValidationError('Date found cannot be more than 1 year ago!')    
        return date_found

    
    def clean(self):
        cleaned_data = super().clean()
        item_type = cleaned_data.get('item_type')
        today = datetime.date.today()
        
        if item_type == 'lost':
            date_lost = cleaned_data.get('date_lost')
            if date_lost and date_lost > today:
                self.add_error('date_lost', 'Date lost cannot be in the future!')
            
            if not cleaned_data.get('location_lost'):
                self.add_error('location_lost', 'Please provide where you lost the item')
            if not date_lost:
                self.add_error('date_lost', 'Please provide when you lost the item')
        else:  # found
            date_found = cleaned_data.get('date_found')
            if date_found and date_found > today:
                self.add_error('date_found', 'Date found cannot be in the future!')
            
            if not cleaned_data.get('location_found'):
                self.add_error('location_found', 'Please provide where you found the item')
            if not date_found:
                self.add_error('date_found', 'Please provide when you found the item')
        
        return cleaned_data