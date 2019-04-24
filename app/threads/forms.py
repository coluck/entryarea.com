import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Thread


class ThreadForm(forms.ModelForm):
    # title = forms.CharField(widget=forms.TextInput(
    #     attrs={"type": "hidden"}),
    #     required=True, max_length=49)
    #
    class Meta:
        model = Thread
        fields = ['title']

    def clean_title(self):
        data = self.data['title'].lower()

        # remove multiple spaces
        data = re.sub(' +', ' ', data)

        if len(data) > 49:
            raise ValidationError(_("invalid title for thread"))

        if data[0] == "@":
            raise ValidationError(_("thread can not start with @"))

        return data


class TitleForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(
        attrs={"type": "hidden"}),
        required=True, max_length=49)

    def clean_title(self):
        # data = self.cleaned_data['title'].lower()
        # data = self.cleaned_data.get('title').lower()

        data = self.data['title'].lower()

        # remove multiple spaces
        data = re.sub(' +', ' ', data)
        # data = " ".join(data.split())

        if len(data) > 49:
            raise ValidationError(_("invalid title for thread"))

        return data
