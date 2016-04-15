# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import eq_
from mock import Mock
from lamvery.clients.base import BaseClient


class TestClient(BaseClient):
    pass


class BaseClientTestCase(TestCase):

    def setUp(self):
        self.client = TestClient(region='us-east-1')
        self.client._sts = Mock()

    def get_account_id(self):
        self.client._sts.get_caller_identity = Mock(return_value={'Account': 'foo'})
        eq_(self.client.get_account_id(), 'foo')
