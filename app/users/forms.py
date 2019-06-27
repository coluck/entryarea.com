from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext as _


from app.users.models import User


class SignUpForm(UserCreationForm):
    # username = forms.CharField(max_length=42, required=True,
    #                            widget=forms.TextInput(attrs={"autocomplete": "off"}),
    #                            help_text="username", label="username")
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput(),
                             help_text="")

    def clean_username(self):
        data = self.cleaned_data['username']
        if not data.islower():
            raise forms.ValidationError(_("username should be in lowercase"))
        return data

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
