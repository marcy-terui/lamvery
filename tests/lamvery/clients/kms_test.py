# -*- coding: utf-8 -*-

import botocore
import base64

from unittest import TestCase
from nose.tools import ok_, eq_
from mock import Mock
from lamvery.clients.kms import KmsClient


class KmsClientTestCase(TestCase):

    def setUp(self):
        self.client = KmsClient(region='us-east-1')
        self.client._kms = Mock()

    def test_encrypt(self):
        self.client._kms.encrypt = Mock(return_value={'CiphertextBlob': 'foo'})
        eq_(self.client.encrypt('key', 'val'), base64.b64encode('foo'))

    def test_decrypt(self):
        self.client._kms.decrypt = Mock(return_value={'Plaintext': 'bar'})
        eq_(self.client.decrypt(base64.b64encode('secret')), 'bar')
