# -*- coding: utf-8 -*-

import os
import sys
import botocore
import base64

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
        self.client = Client(region='us-east-1')
        self.client._lambda = Mock()
        self.client._kms = Mock()

    def test_get_function_conf(self):
        self.client._lambda.get_function = Mock(
            return_value={'Configuration': 'foo'})
        eq_(self.client.get_function_conf('test'), 'foo')
        self.client._lambda.get_function = Mock(
            side_effect=botocore.exceptions.ClientError({'Error': {}}, 'bar'))
        eq_(self.client.get_function_conf('test'), {})

    def test_create_function(self):
        self.client.create_function(Mock(), TEST_CONF, True)

    def test_update_function_code(self):
        self.client.update_function_code(Mock(), TEST_CONF, True)

    def test_update_function_conf(self):
        self.client.update_function_conf(TEST_CONF)

    def test_get_alias(self):
        self.client._lambda.get_alias = Mock(return_value='foo')
        eq_(self.client.get_alias('function', 'alias'), 'foo')
        self.client._lambda.get_alias = Mock(
            side_effect=botocore.exceptions.ClientError({'Error': {}}, 'bar'))
        eq_(self.client.get_alias('function', 'alias'), {})

    def test_create_alias(self):
        self.client.create_alias('function', 'alias', 'version')

    def test_update_alias(self):
        self.client.update_alias('function', 'alias', 'version')

    def test_encrypt(self):
        self.client._kms.encrypt = Mock(return_value={'CiphertextBlob': 'foo'})
        eq_(self.client.encrypt('key', 'val'), base64.b64encode('foo'))

    def test_decrypt(self):
        self.client._kms.decrypt = Mock(return_value={'Plaintext': 'bar'})
        eq_(self.client.decrypt(base64.b64encode('secret')), 'bar')
