import unittest
from test_plus.test import TestCase
from django.conf import settings
from django.utils import timezone

from trax.trax import models, forms, handlers
from trax.users.models import User


class TestForms(TestCase):
    def setUp(self):
        self.user = self.make_user()

    def test_start_timer_handler(self):
        handler = handlers.handlers_by_key['start']
        arguments = 'this is my timer'

        now = timezone.now()
        with unittest.mock.patch('django.utils.timezone', return_value=now):
            result = handler.handle(arguments, user=self.user)

        group = result['timer_group']

        self.assertEqual(group.name, 'this is my timer')
        self.assertEqual(group.slug, 'this-is-my-timer')
        self.assertEqual(group.user, self.user)

        timer = group.timers.first()

        self.assertGreater(timer.start_date, now)
        self.assertEqual(timer.end_date, None)

    def test_stop_timer(self):
        handler = handlers.handlers_by_key['stop']
        group = models.TimerGroup.objects.start('Test 2', user=self.user)

        self.assertTrue(group.is_started)

        result = handler.handle('', user=self.user)
        timer = group.timers.first()

        self.assertFalse(group.is_started)
        self.assertFalse(timer.is_started)

    def test_list_timers(self):
        handler = handlers.handlers_by_key['list']
        group = models.TimerGroup.objects.start('Test 2', user=self.user)

        result = handler.handle('', user=self.user)
        self.assertEqual(len(result['timer_groups']), 1)
        self.assertEqual(result['timer_groups'].first(), group)
