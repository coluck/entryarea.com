import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.translation import get_language as lang

from app.threads.models import Thread
from app.entries.forms import EntryForm


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
        title = get.strip()
        try:
            thread = Thread.objects.get(title=title, lang=lang())
            return redirect(thread)
        except Thread.DoesNotExist:
            form = EntryForm()
            form.fields['body'].widget.attrs['placeholder'] = \
                "enlight us about " + str(title)
            return render(request, 'threads/store.html',
                          {'title': str(title), 'form': form})


def threads(request):
    threads = Thread.objects.all()
    return HttpResponse(threads)
