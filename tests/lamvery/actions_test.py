# -*- coding: utf-8 -*-

import tempfile
import yaml
import os

from unittest import TestCase
from nose.tools import ok_, eq_, raises
from mock import Mock,MagicMock,patch
from lamvery.actions import *

import lamvery.actions

DEFAULT_CONF = """
configuration:
  region: us-east-1
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
        os.remove(self.conf)

    def test_get_conf_data(self):
        actions = Actions(self.conf, True)
        eq_(actions.get_conf_data(), yaml.load(DEFAULT_CONF).get('configuration'))

    def test_get_function_name(self):
        actions = Actions(self.conf, True)
        eq_(actions.get_function_name(), 'test_lambda_function')
        actions = Actions('/foo/bar', True)
        eq_(actions.get_function_name(), os.path.basename(os.getcwd()))

    def test_get_archive_name(self):
        actions = Actions(self.conf, True)
        eq_(actions.get_archive_name(), 'test_lambda_function.zip')

    def test_get_region(self):
        actions = Actions(self.conf, True)
        eq_(actions.get_region(), 'us-east-1')
        actions = Actions('/foo/bar', True)
        eq_(actions.get_region(), None)

    def test_init(self):
        actions = Actions(self.conf, True)
        actions._needs_write_conf = Mock(return_value=True)
        actions._get_default_conf = Mock(return_value={'configuration': {'foo': 'bar'}})
        actions.init()
        eq_(actions.get_conf_data(), {'foo': 'bar'})

    def test_get_default_conf(self):
        actions = Actions(self.conf, True)
        runtime = actions._get_default_conf().get('configuration').get('runtime')
        eq_(runtime, 'python2.7')

    def test_needs_write_conf(self):
        # New
        actions = Actions('/foo/bar', True)
        eq_(actions._needs_write_conf(), True)
        # Overwrite
        actions = Actions(self.conf, True)
        def dummy_y(txt):
            return 'y'
        def dummy_n(txt):
            return 'n'
        # Overwrite yes
        lamvery.actions.raw_input = dummy_y
        eq_(actions._needs_write_conf(), True)
        # Overwrite no
        lamvery.actions.raw_input = dummy_n
        eq_(actions._needs_write_conf(), False)

    def test_archive(self):
        actions = Actions(self.conf, True)
        actions.get_archive_name = Mock(return_value=self.conf)
        actions.archive()

    @patch('lamvery.actions.Client')
    @patch('lamvery.actions.Archive')
    def test_deploy(self, c, a):
        # Dry run
        actions = Actions(self.conf, True)
        actions.print_conf_diff = Mock()
        actions.deploy()

        # No dry run
        actions = Actions(self.conf, False)
        actions.print_conf_diff = Mock()
        # New
        c.get_function_conf = Mock(return_value={})
        actions.deploy()
        # Update
        c.get_function_conf = Mock(return_value={'foo': 'bar'})
        actions.deploy()

    def test_get_conf_diff(self):
        remote = {
            'Runtime': 'python2.7',
            'Role': 'foo',
            'Handler': 'bar',
        }
        local = {
            'runtime': 'python2.7',
            'role': 'bar',
        }
        ret = {
            'runtime': None,
            'role': ('foo', 'bar',),
            'handler': ('bar', None,),
            'description': None,
            'timeout': None,
            'memory_size': None,
        }
        actions = Actions(self.conf, True)
        eq_(actions._get_conf_diff(remote, local), ret)

    def test_print_conf_diff(self):
        remote = {
            'Runtime': 'python2.7',
            'Role': 'foo',
            'Handler': 'bar',
        }
        local = {
            'runtime': 'python2.7',
            'role': 'bar',
        }
        actions = Actions(self.conf, True)
        actions.print_conf_diff(remote, local)
