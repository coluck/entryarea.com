from django import forms

from .models import Entry


class EntryForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'your ea', 'cols': "75%", 'rows': "5"}),
        max_length=50000, required=True, label='')

    class Meta:
        model = Entry
        fields = ['body']
