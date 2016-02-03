# -*- coding: utf-8 -*-

import botocore
import base64

from unittest import TestCase
from nose.tools import ok_, eq_
from mock import Mock
from lamvery.clients.logs import LogsClient


class LogsClientTestCase(TestCase):

    def setUp(self):
        self.client = LogsClient(region='us-east-1')
        self.client._logs = Mock()

    def test_get_log_events(self):
        ret1 = {'events': ['foo', 'bar'], 'NextToken': 'foo'}
        ret2 = {'events': ['baz', 'qux']}
        self.client._logs.filter_log_events = Mock(side_effect=[ret1, ret2])
        eq_(self.client.get_log_events('foo', 123456, 'bar'), ['foo', 'bar', 'baz', 'qux'])
