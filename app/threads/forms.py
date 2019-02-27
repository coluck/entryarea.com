import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Thread


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title']


class TitleForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(
        attrs={"type": "hidden"}),
        required=True, max_length=49)

    def clean_title(self):
        data = self.cleaned_data['title'].lower()

        # remove multiple spaces
        data = re.sub(' +', ' ', data)
        # data = " ".join(data.split())

        if len(data) > 49:
            raise ValidationError(_("invalid title for thread"))

        return data
