# -*- coding: utf-8 -*-

import tempfile
import yaml
import os

from unittest import TestCase
from nose.tools import ok_, eq_, raises
from mock import Mock,MagicMock,patch
from lamvery.config import *

import lamvery.config

DEFAULT_CONF = """
profile: default
region: us-east-1
configuration:
  runtime: python2.7
  name: test_lambda_function
  role: arn:aws:iam::000000000000:role/lambda_basic_execution
  handler: lambda_function.lambda_handler
  description: This is sample lambda function.
  timeout: 10
  memory_size: 128
  test_env: {{ env['PATH'] }}
events:
  - name: foo
    description: This is a sample CloudWatchEvent
    schedule: rate(5 minutes)
secret:
  key_id: arn:aws:kms:<region>:<account-number>:key/<key-id>
  cipher_texts:
    foo: bar
"""

class FunctionsTestCase(TestCase):

    def test_represent_odict(self):
        dumper = Mock()
        dumper.represent_mapping = Mock(return_value='test')
        eq_(represent_odict(dumper, {'foo': 'bar'}), 'test')

class ConfigTestCase(TestCase):

    def setUp(self):
        self.conf_file = '.test.lamvery.yml'
        open(self.conf_file, 'w').write(DEFAULT_CONF)

    def tearDown(self):
        os.remove(self.conf_file)

    def test_load_conf(self):
        config = Config(self.conf_file)
        eq_(config.load_conf().get('profile'), 'default')

    def test_raw_conf(self):
        config = Config(self.conf_file)
        eq_(config.load_raw_conf().get('configuration').get('test_env'), "{{ env['PATH'] }}")

    def test_escape(self):
        config = Config(self.conf_file)
        eq_(config.escape('{{ foo[\'bar\'] }}'), '\'{{ foo[\'\'bar\'\'] }}\'')
        eq_(config.escape('{% foo["bar"] %}'), '\'{% foo["bar"] %}\'')

    def test_get_configuration(self):
        config = Config(self.conf_file)
        eq_(config.get_configuration().get('test_env'), os.environ.get('PATH'))

    def test_get_function_name(self):
        config = Config(self.conf_file)
        eq_(config.get_function_name(), 'test_lambda_function')
        config = Config('/foo/bar')
        eq_(config.get_function_name(), os.path.basename(os.getcwd()))

    def test_get_archive_name(self):
        config = Config(self.conf_file)
        eq_(config.get_archive_name(), 'test_lambda_function.zip')

    def test_get_region(self):
        config = Config(self.conf_file)
        eq_(config.get_region(), 'us-east-1')
        config = Config('/foo/bar')
        eq_(config.get_region(), None)

    def test_get_profile(self):
        config = Config(self.conf_file)
        eq_(config.get_profile(), 'default')

    def test_get_default(self):
        config = Config(self.conf_file)
        runtime = config.get_default().get('configuration').get('runtime')
        eq_(runtime, 'python2.7')

    def test_get_secret(self):
        config = Config(self.conf_file)
        key = config.get_secret().get('key_id')
        eq_(key, 'arn:aws:kms:<region>:<account-number>:key/<key-id>')

    def test_generate_lambda_secret(self):
        config = Config(self.conf_file)
        secret = config.generate_lambda_secret()
        eq_(secret, {
            'region': 'us-east-1',
            'cipher_texts': {
                'foo': 'bar'
            }
        })

    def test_write_default(self):
        config = Config(self.conf_file)
        config.write_default()

    def test_file_exists(self):
        config = Config(self.conf_file)
        eq_(config.file_exists(), True)
        config = Config('/foo/bar')
        eq_(config.file_exists(), False)

    def test_store_secret(self):
        config = Config(self.conf_file)
        config.store_secret('foo', 'bar')
        runtime = config.get_default().get('configuration').get('runtime')
        eq_(config.get_secret().get('cipher_texts').get('foo'), 'bar')

    def test_get_events(self):
        config = Config(self.conf_file)
        eq_(config.get_events().pop().get('schedule'), 'rate(5 minutes)')
        config.load_conf = Mock(return_value={'events': None})
        eq_(config.get_events(), [])
