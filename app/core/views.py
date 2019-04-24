import json
import re

from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import get_language as lang
from django.utils.translation import ugettext as _


from app.threads.models import Thread
from app.threads.forms import TitleForm, ThreadForm
from app.entries.forms import EntryForm
from app.users.models import User
from .forms import ContactForm


from django.core.exceptions import ObjectDoesNotExist
def search(request):
    if request.is_ajax():
        term = request.GET.get('term', '')
        results = []

        queries = Thread.objects.filter(title__icontains=term, lang=lang())[:15]

        for query in queries:
            results.append(query.title)

        res = json.dumps(results)
        mimetype = 'application/json'

        return HttpResponse(res, mimetype)

        # queries = Thread.objects.filter(title__icontains=term, lang=lang()).values()[:15]
        # lis = list(queries)
        # return JsonResponse(lis, safe=False)

    else:
        get = request.GET.get('q')
        data = get.strip()
        title = re.sub(' +', ' ', data)
        try:
            thread = Thread.objects.get(title=title, lang=lang())
            return redirect(thread)
        except Thread.DoesNotExist:  # Don't works
            print("Works")
            form = EntryForm()
            form.fields['body'].widget.attrs['placeholder'] = \
                "enlight us about " + str(title)
            return render(request, 'threads/store.html', {'title': str(title), 'form': form})
            # return redirect("thread:new", title=title)


def Search(request):
    num = 10
    if request.is_ajax():
        term = request.GET.get('term', '')
        results = []

        if str(term[0]) == '@':
            queries = User.objects.filter(username__icontains=term[1:])[:num]
            for query in queries:
                results.append("@" + query.username)
        else:
            queries = Thread.objects.filter(title__icontains=term, lang=lang())[:num]
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

        elif data[0] == '#':
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


def contact(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            from_email = form.cleaned_data['from_email']
            message_with_email = f"From: {from_email} \n" + message
            try:
                send_mail(subject, message_with_email, from_email,
                          ['gencineer@gmail.com'])  # TODO: change mail
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('core:success')
    return render(request, "app/contact.html", {'form': form})


def success(request):
    messages.success(request, _("your message sent successfully"))
    return redirect('/')
