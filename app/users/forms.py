from django import forms
from django.contrib.auth.forms import UserCreationForm

from app.users.models import User


class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=42, required=True,
                               widget=forms.TextInput(attrs={"autocomplete": "off"}),
                               help_text="username", label="nick")
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
