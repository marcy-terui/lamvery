# -*- coding: utf-8 -*-

import os
import sys
import botocore

from unittest import TestCase
from nose.tools import ok_, eq_, raises
from mock import Mock,MagicMock,patch
from lamvery.client import *

TEST_CONF = {
  'runtime': 'python2.7',
  'name': 'test_lambda_function',
  'role': 'arn:aws:iam::000000000000:role/lambda_basic_execution',
  'handler': 'lambda_function.lambda_handler',
  'description': 'This is sample lambda function.',
  'timeout': 10,
  'memory_size': 128,
  'publish': True
}

class ClientTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.client._client = Mock()

    def test_get_function_conf(self):
        self.client._client.get_function = Mock(
            return_value={'Configuration': 'foo'})
        eq_(self.client.get_function_conf('test'), 'foo')
        self.client._client.get_function = Mock(
            side_effect=botocore.exceptions.ClientError({'Error': {}}, 'bar'))
        eq_(self.client.get_function_conf('test'), {})

    def test_create_function(self):
        self.client.create_function(Mock(), TEST_CONF)

    def test_update_function_code(self):
        self.client.update_function_code(Mock(), TEST_CONF)

    def test_update_function_conf(self):
        self.client.update_function_conf(TEST_CONF)
