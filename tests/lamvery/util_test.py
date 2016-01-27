# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import ok_, eq_, raises
from mock import Mock,MagicMock,patch

from lamvery.utils import *

class UtilsActionTestCase(TestCase):

    def test_previous_alias(self):
        eq_(previous_alias('foo'), 'foo-pre')
