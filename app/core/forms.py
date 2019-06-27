from django import forms
# from .models import ContactMessage
from app.core.models import ContactMessage


class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(required=True, widget=forms.Textarea)


class ContactMessageForm(forms.ModelForm):
    # message = forms.Textarea()
    # message_type = forms.ChoiceField(choices=ContactMessage.MESSAGE_TYPE)
    # email = forms.EmailField(required=True)

    class Meta:
        model = ContactMessage
        # exclude = ["user"]
        fields = ["subject", "message", "email"]
