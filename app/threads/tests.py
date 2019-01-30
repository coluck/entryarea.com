from django.test import TestCase
from django.utils import timezone

from entries.models import Entry
from users.models import User
from .models import Thread

'''
class ThreadTestCase(TestCase):
    def setUp(self):
        User.objects.create(username="admin",
                            password="password",
                            email="admin@mail.com")

        Thread.objects.create(title="thread",
                              user=User.objects.get(username="admin"),
                              created_at=timezone.now, lang="en")

        Entry.objects.create(body="Test body",
                             user=User.objects.get(username="admin"),
                             created_at=timezone.now, lang="en",
                             thread=Thread.objects.get(title="thread"))

    def test_thread_has_counter(self):
        thread = Thread.objects.get(title="thread")
        cnt = thread.get_entry_count()
        self.assertEqual(cnt, 1)


'''
