# -*- coding: utf-8 -*-

import tempfile
import yaml
from unittest import TestCase
from nose.tools import ok_, eq_, raises
from mock import Mock,MagicMock,patch
from lamvery.actions import *

DEFAULT_CONF = """
configuration:
  runtime: python2.7
  name: test_lambda_function
  role: arn:aws:iam::000000000000:role/lambda_basic_execution
  handler: lambda_function.lambda_handler
  description: This is sample lambda function.
  timeout: 10
  memory_size: 128
  publish: true
"""

class FunctionsTestCase(TestCase):

    def test_represent_odict(self):
        dumper = Mock()
        dumper.represent_mapping = Mock(return_value='test')
        eq_(represent_odict(dumper, {'foo': 'bar'}), 'test')

class ActionsTestCase(TestCase):

    def setUp(self):
        tmp = tempfile.mkstemp(prefix=__name__)
        open(tmp[1], 'w').write(DEFAULT_CONF)
        self.conf = tmp[1]

    def tearDown(self):
        pass

    def test_get_conf_data(self):
        actions = Actions(self.conf, True)
        eq_(actions.get_conf_data(), yaml.load(DEFAULT_CONF).get('configuration'))

    def test_get_function_name(self):
        actions = Actions(self.conf, True)
        eq_(actions.get_function_name(), 'test_lambda_function')

    def test_get_archive_name(self):
        actions = Actions(self.conf, True)
        eq_(actions.get_archive_name(), 'test_lambda_function.zip')
