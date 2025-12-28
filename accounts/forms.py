# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm , UserChangeForm
from .models import CustomUser , Report

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email address'
    }))
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'student_id', 'phone_number', 'profile_picture', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student ID (if applicable)'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'student_id', 
            'bio',
            'profile_picture'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell us a bit about yourself...'
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': '+1234567890'
            }),
            'student_id': forms.TextInput(attrs={
                'placeholder': 'e.g., S12345678'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields required or optional as needed
        self.fields['student_id'].required = False
        self.fields['phone_number'].required = False
        self.fields['email'].required = True
        
class UserTypeUpdateForm(forms.ModelForm):
    """Form for updating user type (admin only)"""
    class Meta:
        model = CustomUser
        fields = ['user_type']
        widgets = {
            'user_type': forms.Select(attrs={
                'class': 'form-select'
            })
        }

class DeleteProfilePictureForm(forms.Form):
    """Simple form for deleting profile picture"""
    confirm = forms.BooleanField(
        required=True,
        label="I want to delete my profile picture",
        help_text="This action cannot be undone."
    )

class ReportForm(forms.ModelForm):
    """Form for submitting reports"""
    class Meta:
        model = Report
        fields = ['report_type', 'description', 'content_type', 'content_id']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Please provide details about the issue...'
            }),
            'content_type': forms.TextInput(attrs={
                'placeholder': 'e.g., product, user, lostFounditem'
            }),
            'content_id': forms.NumberInput(attrs={
                'placeholder': 'ID of the content being reported'
            }),
        }