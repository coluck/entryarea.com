import json
import re

from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.translation import get_language as lang

from app.threads.models import Thread
from app.entries.forms import EntryForm
from app.users.models import User
from core.forms import ContactForm


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
        except Thread.DoesNotExist:
            form = EntryForm()
            form.fields['body'].widget.attrs['placeholder'] = \
                "enlight us about " + str(title)
            # return render(request, 'threads/store.html', {'title': str(title), 'form': form})
            return redirect("thread:new", title=title)


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
            user = User.objects.get(username=data)
            return redirect(user)

        elif data[0] == '#':
            return redirect("entry:read", pk=data[1:])

        else:
            title = re.sub(' +', ' ', data)
            try:
                thread = Thread.objects.get(title=title, lang=lang())
                return redirect(thread)
            except Thread.DoesNotExist:
                form = EntryForm()
                form.fields['body'].widget.attrs['placeholder'] = \
                    "write something to create this thread"
                return render(request, 'threads/store.html',
                              {'title': str(title), 'form': form})


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
    return HttpResponse('Success! Thank you for your message.')
