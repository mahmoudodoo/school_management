# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'your@email.com',
            'autocomplete': 'email'
        })
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '+1234567890'
        })
    )
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'select-field'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'user_type', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set placeholders for password fields
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm password'})
        
        # Apply CSS classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'input-field',
                'data-validate': str(field.required).lower()
            })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
        return user
