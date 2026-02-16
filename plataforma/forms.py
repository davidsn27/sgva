"""
Django forms for authentication and data validation.
"""

from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form for signup."""

    class Meta:
        model = User
        fields = ("username", "email")


class CustomUserChangeForm(UserChangeForm):
    """Custom user change form for profile updates."""

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")


class CustomSignupForm(SignupForm):
    """Custom signup form extending allauth SignupForm."""

    first_name = forms.CharField(
        max_length=30,
        label="Nombre",
        widget=forms.TextInput(attrs={"placeholder": "Tu nombre"}),
    )
    last_name = forms.CharField(
        max_length=30,
        label="Apellido",
        widget=forms.TextInput(attrs={"placeholder": "Tu apellido"}),
    )

    def save(self, request):
        """Save user with additional fields."""
        user = super().save(request)
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.save()
        return user
