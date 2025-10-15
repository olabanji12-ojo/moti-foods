from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Customer

class CustomerCreationForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = ['username', 'name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter username...'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email...'}),
        }
        help_texts = {
            'username': None,
            'password1': None,
            'password2': None,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Clear help texts for all fields
        for field in self.fields.values():
            field.help_text = None


class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#F4C430] focus:border-transparent text-[#3E3E3E]',
            'placeholder': 'Enter your email',
        })
    )

class SetPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#F4C430] focus:border-transparent text-[#3E3E3E]',
            'placeholder': 'Enter new password',
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#F4C430] focus:border-transparent text-[#3E3E3E]',
            'placeholder': 'Confirm new password',
        })
    )


