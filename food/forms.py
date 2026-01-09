# food/forms.py
from django import forms
from .models import FoodVendor, MenuItem, FoodReview

class FoodVendorForm(forms.ModelForm):
    # Hidden fields for coordinates (set by map JavaScript)
    latitude = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=8,
        widget=forms.HiddenInput(attrs={'id': 'id_latitude'})
    )
    
    longitude = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=8,
        widget=forms.HiddenInput(attrs={'id': 'id_longitude'})
    )
    
    class Meta:
        model = FoodVendor
        fields = [
            'vendor_type', 'name', 'description', 'cuisine_type',
            'address', 'city', 'neighborhood', 'latitude', 'longitude',
            'phone', 'email', 'website',
            'opening_time', 'closing_time',
            'delivery_available', 'takeaway_available', 'dine_in_available',
            'accepts_card', 'wifi_available',
            'main_image', 'image_2', 'image_3'
        ]
        widgets = {
            'vendor_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'cuisine_type': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'opening_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'main_image': forms.FileInput(attrs={'class': 'form-control'}),
            'image_2': forms.FileInput(attrs={'class': 'form-control'}),
            'image_3': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
    def save(self, commit=True):
        instance = super().save(commit=False)
    
    # Get coordinates from form fields
        latitude = self.cleaned_data.get('latitude')
        longitude = self.cleaned_data.get('longitude')
    
        print(f"Saving coordinates: Lat={latitude}, Lng={longitude}")  # Debug line
    
        if latitude and longitude:
        # Round to 6 decimal places to match model
            instance.latitude = round(float(latitude), 6)
            instance.longitude = round(float(longitude), 6)
    
    # Clean amenities - ensure proper formatting
        if 'amenities' in self.cleaned_data and self.cleaned_data['amenities']:
        # Split by commas, strip whitespace, and join back
            amenities_list = [amenity.strip() for amenity in self.cleaned_data['amenities'].split(',')]
            instance.amenities = ', '.join(amenities_list)
    
        if commit:
            instance.save()
        return instance    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values for coordinates if editing
        instance = kwargs.get('instance')
        if instance:
            self.fields['latitude'].initial = instance.latitude
            self.fields['longitude'].initial = instance.longitude


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'category', 'price', 'image', 'is_available', 'is_popular']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class FoodReviewForm(forms.ModelForm):
    class Meta:
        model = FoodReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Share your experience...'}),
        }


class FoodSearchForm(forms.Form):
    """Form for searching food vendors"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search restaurants...'
        })
    )
    
    cuisine_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Cuisines')] + FoodVendor.CUISINE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    vendor_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + FoodVendor.VENDOR_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    delivery_available = forms.ChoiceField(
        required=False,
        choices=[('', 'Any'), ('yes', 'Delivery Available'), ('no', 'No Delivery')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('newest', 'Newest First'),
            ('rating', 'Highest Rated'),
            ('popular', 'Most Popular'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='newest'
    )