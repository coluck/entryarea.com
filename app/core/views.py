import json
import re

import pytz
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.utils.translation import get_language as lang

from app.entries.forms import EntryForm
from app.threads.forms import ThreadForm
from app.threads.models import Thread
from app.users.models import User

from .forms import ContactForm, ContactMessageForm

NUM = 10


def search(request):
    if request.is_ajax():
        term = request.GET.get('term', '')
        results = []

        if str(term[0]) == '@':
            queries = User.objects.filter(username__icontains=term[1:])[:NUM]
            for query in queries:
                results.append("@" + query.username)
        else:
            queries = Thread.objects.filter(title__icontains=term, lang=lang())[:NUM]
            for query in queries:
                results.append(query.title)

        res = json.dumps(results)
        mimetype = 'application/json'

        return HttpResponse(res, mimetype)
    else:
        get = request.GET.get('q')
        data = get.strip()
        if data[0] == '@':
            user = User.objects.get(username=data[1:])
            return redirect(reverse("user:profile", args=[user.username]))

        elif data[0] == '#' and data[1:].isnumeric():
            return redirect("entry:read", pk=data[1:])

        else:
            title = re.sub(' +', ' ', data)
            try:
                thread = Thread.objects.get(title=title, lang=lang())
                return redirect(thread)
            except ObjectDoesNotExist:
                eform = EntryForm()
                tform = ThreadForm({'title': title})

                eform.fields['body'].widget.attrs['placeholder'] = \
                    "write something to create this thread"
                if tform.is_valid():
                    return render(request, 'threads/store.html',
                                  {'title': title, 'eform': eform, 'tform': tform})
                return render(request, 'threads/store.html',
                              {'title': title, 'error': True})


# def contact_email(request):
#     if request.method == 'GET':
#         form = ContactForm()
#     else:
#         form = ContactForm(request.POST)
#         if form.is_valid():
#             subject = form.cleaned_data['subject']
#             message = form.cleaned_data['message']
#             from_email = form.cleaned_data['from_email']
#             message_with_email = f"From: {from_email} \n" + message
#             try:
#                 send_mail(subject, message_with_email, from_email,
#                           ['gencineer@gmail.com'])
#             except BadHeaderError:
#                 return HttpResponse('Invalid header found.')
#             return redirect('core:success')
#     return render(request, "app/contact.html", {'form': form})


def contact(request):
    if request.method == 'GET':
        sub = request.GET.get("subject", "")
        # print(type)
        message = request.GET.get("message", None)
        # print(message)
        form = ContactMessageForm(initial={"subject": str(sub),
                                           "message": message})
    else:
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            if request.user.is_authenticated:
                contact_message.user = request.user
            contact_message.lang = lang()
            contact_message.save()
            messages.success(request, _('your message sent successfully'))
            return redirect("/")
    return render(request, "app/contact.html", {'form': form})


def set_timezone(request):  # May add user specific timezone
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('/')
    else:
        return render(request, 'auth/set-timezone.html',
                      {'timezones': pytz.common_timezones})
