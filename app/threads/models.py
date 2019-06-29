import datetime
import math

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.urls import reverse

from app.core.models import SoftDeletionModel

PAGINATE = 10
MAX_LEN = 64


class Thread(SoftDeletionModel):
    title = models.CharField(max_length=MAX_LEN)
    lang = models.CharField(choices=settings.LANGUAGES, max_length=2)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField("Tag", blank=True, related_name='threads')
    views = models.PositiveIntegerField(default=0)

    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    last_entry = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['last_entry']),
        ]
        ordering = ['-last_entry']

        unique_together = ('title', 'lang')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # If model is updating on admin, there should be modification in slug
        if self.slug:
            self.slug = slugify(self.title, allow_unicode=True) + "--" + str(self.id)

        # Save the thread in order to get the id to append in the slug
        super(Thread, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True) + "--" + str(self.id)
            self.save()

    def get_absolute_url(self):
        return reverse('thread:read', args=[self.slug])

    def get_entry_count(self):
        """ Get the total entry count in the thread """
        return self.entries.count()

    @property
    def get_today_entry_count(self):
        """ Get today entry count in the thread """
        return self.entries \
            .filter(created_at__startswith=datetime.date.today()).count()

    def get_tag_count(self):
        return self.tags.count()

    def get_page_count(self):
        count = self.get_entry_count()
        pages = count / PAGINATE
        return math.ceil(pages)

    def get_date(self):
        return str(self.created_at.day) + '-' + str(self.created_at.month) + \
            '-' + str(self.created_at.year)


class Tag(models.Model):
    label = models.CharField(max_length=30)
    slug = models.SlugField(max_length=35, unique=True, blank=True)
    descr = models.CharField(max_length=100, blank=True)
    lang = models.CharField(choices=settings.LANGUAGES, max_length=2)

    def __str__(self):
        return f"{self.label}({self.lang})"

    def save(self, *args, **kwargs):
        if self.slug:
            self.slug = slugify(self.label)

        tag_with_same_slug = Tag.objects.filter(slug=self.slug)

        if tag_with_same_slug.exists():
            self.slug = slugify(self.label) + "--" + str(self.lang)
        #
        # # Save the tag if slug not exists
        super(Tag, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(self.label)
            self.save()

    def get_absolute_url(self):
        return reverse('thread:tag-read', args=[self.slug])

    def get_thread_count(self):
        return self.threads.count()
