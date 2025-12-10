from django import forms
from .models import Product, Offer
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import datetime

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title', 'description', 'category', 'condition', 'price', 'negotiable', 'fixed_price',
            'image1', 'image2', 'image3', 'image4', 'contact_phone', 'contact_email',
            'location', 'meetup_preference', 'brand', 'model', 'warranty_remaining',
            'purchase_date', 'original_price'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Describe your item in detail...'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., MacBook Air M1 2020'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Main Campus Library'}),
            'meetup_preference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Where do you prefer to meet?'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brand name (if applicable)'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Model (if applicable)'}),
            'warranty_remaining': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Months'}),
            'purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'max': datetime.date.today().isoformat()}),
            'original_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'placeholder': 'Original price (if known)'}),
        }
        labels = {
            'image1': 'Main Image *',
            'image2': 'Additional Image 1',
            'image3': 'Additional Image 2',
            'image4': 'Additional Image 3',
            'negotiable': 'Price is negotiable',
            'fixed_price': 'This is a fixed price item',
        }
    
    def clean_image1(self):
        image = self.cleaned_data.get('image1')
        if image:
            # Check file size (Cloudinary free tier: 10MB max)
            if image.size > 10 * 1024 * 1024:  # 10MB
                raise forms.ValidationError('Image size must be less than 10MB')
            # Check file type
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            if not any(image.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError('Unsupported file format. Use JPG, PNG, GIF, or WebP.')
        return image    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = datetime.date.today()
        
        # Set max date for purchase_date
        self.fields['purchase_date'].widget.attrs['max'] = today.isoformat()
        
        # Make main image required for new products
        if not self.instance.pk:
            self.fields['image1'].required = True
        else:
            self.fields['image1'].required = False

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError('Price must be greater than 0.')
        return price

    def clean_original_price(self):
        original_price = self.cleaned_data.get('original_price')
        price = self.cleaned_data.get('price')
        
        if original_price and price:
            if original_price <= price:
                raise forms.ValidationError('Original price must be higher than selling price.')
        return original_price

    def clean_purchase_date(self):
        purchase_date = self.cleaned_data.get('purchase_date')
        if purchase_date:
            today = datetime.date.today()
            if purchase_date > today:
                raise forms.ValidationError('Purchase date cannot be in the future.')
        return purchase_date

    def clean(self):
        cleaned_data = super().clean()
        negotiable = cleaned_data.get('negotiable')
        fixed_price = cleaned_data.get('fixed_price')
        
        if negotiable and fixed_price:
            raise forms.ValidationError('An item cannot be both negotiable and fixed price. Please choose one.')
        
        return cleaned_data

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['amount', 'message']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'message': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Optional message to seller...'}),
        }
        labels = {
            'amount': 'Your Offer Amount ($)',
            'message': 'Message to Seller',
        }

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        
        if self.product:
            self.fields['amount'].validators.append(MinValueValidator(self.product.price * 0.5))
            self.fields['amount'].help_text = f'Minimum offer: ${self.product.price * 0.5:.2f}'

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if self.product and amount:
            if amount <= 0:
                raise forms.ValidationError('Offer amount must be greater than 0.')
            if amount > self.product.price * 2:
                raise forms.ValidationError('Offer amount cannot be more than double the asking price.')
        return amount

class ProductFilterForm(forms.Form):
    """Form for filtering products."""
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search products...'
    }))
    
    category = forms.ChoiceField(
        required=False,
        choices=[('', 'All Categories')] + Product.CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    condition = forms.ChoiceField(
        required=False,
        choices=[('', 'Any Condition')] + Product.CONDITION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min', 'step': '0.01'})
    )
    
    max_price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max', 'step': '0.01'})
    )
    
    negotiable = forms.ChoiceField(
        required=False,
        choices=[('', 'Any'), ('yes', 'Negotiable Only'), ('no', 'Fixed Price Only')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('newest', 'Newest First'),
            ('oldest', 'Oldest First'),
            ('price_low', 'Price: Low to High'),
            ('price_high', 'Price: High to Low'),
            ('views', 'Most Viewed'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )