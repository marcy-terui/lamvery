# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import eq_

from lamvery.utils import previous_alias


class UtilsActionTestCase(TestCase):

    def test_previous_alias(self):
        eq_(previous_alias('foo'), 'foo-pre')
