# housing/forms.py
from django import forms
from django.utils import timezone
from .models import HousingListing, FavoriteListing

class HousingListingForm(forms.ModelForm):
    # Custom date input
    available_from = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().date().isoformat(),
        }),
        initial=timezone.now().date(),
        help_text="Select when the property becomes available"
    )
    
    # Amenities as textarea
    amenities = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Wi-Fi, Parking, Gym, Pool, Laundry, etc.'
        }),
        help_text="Comma-separated list of amenities"
    )
    
    # Hidden fields for coordinates - INCREASED max_digits to handle negative signs
    latitude = forms.DecimalField(
        required=False,
        max_digits=12,  # Increased from 9 to 12
        decimal_places=8,  # Increased from 6 to 8
        widget=forms.HiddenInput(attrs={'id': 'id_latitude'})
    )
    
    longitude = forms.DecimalField(
        required=False,
        max_digits=12,  # Increased from 9 to 12
        decimal_places=8,  # Increased from 6 to 8
        widget=forms.HiddenInput(attrs={'id': 'id_longitude'})
    )
    
    class Meta:
        model = HousingListing
        fields = [
            'listing_type', 'property_type', 'title', 'description', 
            'address', 'city', 'neighborhood', 'latitude', 'longitude',
            'price', 'price_period',
            'deposit', 'utilities_included', 'bedrooms', 'bathrooms',
            'square_meters', 'furnished', 'available_from', 'lease_duration',
            'amenities', 'contact_name', 'contact_phone', 'contact_email',
            'contact_preference', 'main_image', 'image_2', 'image_3', 'image_4'
        ]
        widgets = {
            'listing_type': forms.Select(attrs={'class': 'form-select'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_period': forms.Select(attrs={'class': 'form-select'}),
            'deposit': forms.NumberInput(attrs={'class': 'form-control'}),
            'utilities_included': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'square_meters': forms.NumberInput(attrs={'class': 'form-control'}),
            'furnished': forms.Select(attrs={'class': 'form-select'}),
            'lease_duration': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 1 year, 6 months'
            }),
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_preference': forms.Select(attrs={'class': 'form-select'}),
            'main_image': forms.FileInput(attrs={'class': 'form-control'}),
            'image_2': forms.FileInput(attrs={'class': 'form-control'}),
            'image_3': forms.FileInput(attrs={'class': 'form-control'}),
            'image_4': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set HTML5 date attributes
        self.fields['available_from'].widget.attrs['min'] = timezone.now().date().isoformat()
        
        # Set initial values for coordinates if editing
        instance = kwargs.get('instance')
        if instance:
            # Ensure we get the values as Decimal or None
            if instance.latitude:
                self.fields['latitude'].initial = str(instance.latitude)
            if instance.longitude:
                self.fields['longitude'].initial = str(instance.longitude)
        
        # Add placeholder to address field
        self.fields['address'].widget.attrs['placeholder'] = 'e.g., 123 Main Street, Westlands'
        self.fields['city'].widget.attrs['placeholder'] = 'e.g., Nairobi'
        
        # Make sure required fields have proper styling
        for field_name, field in self.fields.items():
            if field.required and hasattr(field.widget, 'attrs'):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' required'
    
    def clean_latitude(self):
        """Clean latitude field"""
        latitude = self.cleaned_data.get('latitude')
        if latitude:
            # Ensure latitude is within valid range (-90 to 90)
            if latitude < -90 or latitude > 90:
                raise forms.ValidationError("Latitude must be between -90 and 90 degrees")
        return latitude
    
    def clean_longitude(self):
        """Clean longitude field"""
        longitude = self.cleaned_data.get('longitude')
        if longitude:
            # Ensure longitude is within valid range (-180 to 180)
            if longitude < -180 or longitude > 180:
                raise forms.ValidationError("Longitude must be between -180 and 180 degrees")
        return longitude
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Get coordinates from form fields
        latitude = self.cleaned_data.get('latitude')
        longitude = self.cleaned_data.get('longitude')
        
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
    
    # Keep all other clean methods...
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError("Price must be greater than 0")
        return price
    
    def clean_bathrooms(self):
        bathrooms = self.cleaned_data.get('bathrooms')
        if bathrooms and bathrooms <= 0:
            raise forms.ValidationError("Number of bathrooms must be greater than 0")
        return bathrooms
    
    def clean_bedrooms(self):
        bedrooms = self.cleaned_data.get('bedrooms')
        if bedrooms and bedrooms <= 0:
            raise forms.ValidationError("Number of bedrooms must be greater than 0")
        if bedrooms and bedrooms > 20:
            raise forms.ValidationError("Number of bedrooms cannot exceed 20")
        return bedrooms
    
    def clean_deposit(self):
        deposit = self.cleaned_data.get('deposit')
        if deposit and deposit < 0:
            raise forms.ValidationError("Deposit cannot be negative")
        return deposit

class HousingSearchForm(forms.Form):
    """Form for searching housing listings"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search listings...'
        })
    )
    
    listing_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + HousingListing.LISTING_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    property_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Properties')] + HousingListing.PROPERTY_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    
    min_price = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'min': 0
        })
    )
    
    max_price = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'min': 0
        })
    )
    
    bedrooms = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bedrooms',
            'min': 1
        })
    )
    
    furnished = forms.ChoiceField(
        required=False,
        choices=[('', 'Any')] + HousingListing.FURNISHED_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    utilities_included = forms.ChoiceField(
        required=False,
        choices=[('', 'Any'), ('yes', 'Utilities Included'), ('no', 'Utilities Not Included')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('newest', 'Newest First'),
            ('price_low', 'Price: Low to High'),
            ('price_high', 'Price: High to Low'),
            ('bedrooms', 'Most Bedrooms'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='newest'
    )