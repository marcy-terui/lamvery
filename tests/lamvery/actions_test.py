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
  alias:
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
        self.conf_file = tmp[1]

    def get_default_args(self):
        args = Mock()
        args.conf_file = self.conf_file
        args.dry_run = True
        args.alias = None
        args.alias_version = None
        return args

    def tearDown(self):
        os.remove(self.conf_file)

    def test_get_conf_data(self):
        actions = Actions(self.get_default_args())
        eq_(actions.get_conf_data(), yaml.load(DEFAULT_CONF).get('configuration'))

    def test_get_function_name(self):
        actions = Actions(self.get_default_args())
        eq_(actions.get_function_name(), 'test_lambda_function')
        args = self.get_default_args()
        args.conf_file = '/foo/bar'
        actions = Actions(args)
        eq_(actions.get_function_name(), os.path.basename(os.getcwd()))

    def test_get_archive_name(self):
        actions = Actions(self.get_default_args())
        eq_(actions.get_archive_name(), 'test_lambda_function.zip')

    def test_get_region(self):
        actions = Actions(self.get_default_args())
        eq_(actions.get_region(), 'us-east-1')
        args = self.get_default_args()
        args.conf_file = '/foo/bar'
        actions = Actions(args)
        eq_(actions.get_region(), None)

    def test_get_alias_name(self):
        actions = Actions(self.get_default_args())
        eq_(actions.get_alias_name(), None)
        args = self.get_default_args()
        args.alias = 'foo'
        actions = Actions(args)
        eq_(actions.get_alias_name(), 'foo')

    def test_get_alias_version(self):
        actions = Actions(self.get_default_args())
        eq_(actions.get_alias_version(), '$LATEST')
        args = self.get_default_args()
        args.alias_version = '1'
        actions = Actions(args)
        eq_(actions.get_alias_version(), '1')

    def test_init(self):
        actions = Actions(self.get_default_args())
        actions._needs_write_conf = Mock(return_value=True)
        actions._get_default_conf = Mock(return_value={'configuration': {'foo': 'bar'}})
        actions.init()
        eq_(actions.get_conf_data(), {'foo': 'bar'})

    def test_get_default_conf(self):
        actions = Actions(self.get_default_args())
        runtime = actions._get_default_conf().get('configuration').get('runtime')
        eq_(runtime, 'python2.7')

    def test_needs_write_conf(self):
        # New
        args = self.get_default_args()
        args.conf_file = '/foo/bar'
        actions = Actions(args)
        eq_(actions._needs_write_conf(), True)
        # Overwrite
        actions = Actions(self.get_default_args())
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
        actions = Actions(self.get_default_args())
        actions.get_archive_name = Mock(return_value=self.conf_file)
        actions.archive()

    @patch('lamvery.actions.Client')
    @patch('lamvery.actions.Archive')
    def test_deploy(self, c, a):
        # Dry run
        actions = Actions(self.get_default_args())
        actions.print_conf_diff = Mock()
        actions.set_alias = Mock()
        actions.deploy()

        # No dry run
        args = self.get_default_args()
        args.dry_run = False
        actions = Actions(args)
        actions.print_conf_diff = Mock()
        actions.set_alias = Mock()
        # New
        c.get_function_conf = Mock(return_value={})
        actions.deploy()
        # Update
        c.get_function_conf = Mock(return_value={'foo': 'bar'})
        actions.deploy()

    @patch('lamvery.actions.Client')
    def test_alias(self, c):
        # No alias
        actions = Actions(self.get_default_args())
        actions.set_alias()

        # Dry run
        args = self.get_default_args()
        args.alias = 'foo'
        actions = Actions(args)
        actions.set_alias()

        # No dry run
        args = self.get_default_args()
        args.alias = 'foo'
        args.dry_run = False
        # New
        c.get_alias = Mock(return_value={})
        actions = Actions(args)
        actions.set_alias()
        # Update
        c.get_alias.return_value = {'FunctionVersion': '1'}
        actions = Actions(args)
        actions.set_alias()


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
        actions = Actions(self.get_default_args())
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
        actions = Actions(self.get_default_args())
        actions.print_conf_diff(remote, local)
