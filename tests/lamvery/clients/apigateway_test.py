# -*- coding: utf-8 -*-

import botocore

from unittest import TestCase
from nose.tools import eq_
from mock import Mock
from lamvery.clients.apigateway import ApiGatewayClient


class ApiGatewayClientTestCase(TestCase):

    def setUp(self):
        self.client = ApiGatewayClient(region='us-east-1')
        self.client._api = Mock()

    def test_get_rest_api(self):
        self.client._api.get_rest_api = Mock(return_value={'foo': 'bar'})
        eq_(self.client.get_rest_api(None), None)
        eq_(self.client.get_rest_api('baz'), {'foo': 'bar'})

        self.client._api.get_rest_api = Mock(
            side_effect=botocore.exceptions.ClientError({'Error': {}}, 'bar'))
        eq_(self.client.get_rest_api('baz'), None)

    def test_get_export(self):
        m = Mock()
        m.read = Mock(return_value='{"foo": "bar"}')
        self.client._api.get_export = Mock(return_value={'body': m})
        eq_(self.client.get_export(None, 'baz'), {})
        eq_(self.client.get_export('baz', 'qux'), {'foo': 'bar'})

        self.client._api.get_export = Mock(
            side_effect=botocore.exceptions.ClientError({'Error': {}}, 'bar'))
        eq_(self.client.get_export('baz', 'qux'), {})

    def test_import_rest_api(self):
        self.client._api.import_rest_api = Mock(return_value={'foo': 'bar'})
        eq_(self.client.import_rest_api({'baz': 'qux'}), {'foo': 'bar'})

    def test_put_rest_api(self):
        self.client._api.put_rest_api = Mock(return_value={'foo': 'bar'})
        eq_(self.client.put_rest_api('foo', {'baz': 'qux'}), {'foo': 'bar'})

    def test_delete_rest_api(self):
        self.client._api.delete_rest_api = Mock()
        self.client.delete_rest_api('foo')

    def test_create_deployment(self):
        self.client._api.create_deployment = Mock(return_value={'foo': 'bar'})
        eq_(self.client.create_deployment('baz', 'qux'), {'foo': 'bar'})
