from django.contrib.sitemaps import Sitemap
from app.threads.models import Thread


class EASitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.5
    protocol = "https"

    def items(self):
        return Thread.objects.all()

    def lastmod(self, obj):
        return obj.last_entry
