import bleach

from django import forms

from .models import Entry


class EntryForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(
        attrs={'required': "true", 'cols': "75%", 'rows': "5",
               "id": "entryarea", "spellcheck": "false"}),
        max_length=50000, required=True, label='')

    class Meta:
        model = Entry
        fields = ['body']


class BodyForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'your ea', 'cols': "75%", 'rows': "5"}),
        max_length=50000, required=True, label='')

    def clean_body(self):
        data = self.cleaned_data['body'].lower()
        # r = bleach.clean(data, tags=['a'], attributes={}, styles=[])
        return data
