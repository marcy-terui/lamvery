# -*- coding: utf-8 -*-

import tempfile
import yaml
import os

from unittest import TestCase
from nose.tools import ok_, eq_, raises
from mock import Mock,MagicMock,patch
from lamvery.actions import *
import lamvery.actions

def default_args():
    args = Mock()
    args.conf_file = '.lamvery.yml'
    args.dry_run = True
    args.alias = None
    args.alias_version = None
    args.text = 'foo'
    args.secret_name = 'bar'
    args.store = True
    return args

class BaseActionTestCase(TestCase):

    @raises(TypeError)
    def test_action(self):
        BaseAction(default_args())

    def test_get_client(self):
        class TestAction(BaseAction):
            def action(self):
                pass
        TestAction(default_args()).get_client()

class InitActionTestCase(TestCase):

    def test_action(self):
        action = InitAction(default_args())
        action._config = Mock()
        action._needs_write_conf = Mock(return_value=True)
        action.action()

    def test_needs_write_conf(self):
        # New
        args = default_args()
        args.conf_file = '/foo/bar'
        action = InitAction(args)
        eq_(action._needs_write_conf(), True)
        # Overwrite
        action = InitAction(default_args())
        def dummy_y(txt):
            return 'y'
        def dummy_n(txt):
            return 'n'
        # Overwrite yes
        lamvery.actions.raw_input = dummy_y
        eq_(action._needs_write_conf(), True)
        # Overwrite no
        lamvery.actions.raw_input = dummy_n
        eq_(action._needs_write_conf(), False)

class ArchiveActionTestCase(TestCase):

    def tearDown(self):
        if os.path.exists('test.zip'):
            os.remove('test.zip')

    def test_action(self):
        action = ArchiveAction(default_args())
        action._config = Mock()
        action._config.get_archive_name = Mock(return_value='test.zip')
        action._config.generate_lambda_secret = Mock(return_value={})
        action.action()
        ok_(os.path.exists('test.zip'))

class DeployActionTestCase(TestCase):

    @patch('lamvery.actions.SetAliasAction')
    @patch('lamvery.actions.Client')
    def test_action(self, a, c):
        # Dry run
        action = DeployAction(default_args())
        action._print_conf_diff = Mock()
        action.action()

        # No dry run
        args = default_args()
        args.dry_run = False
        action = DeployAction(args)
        action._print_conf_diff = Mock()
        # New
        c.get_function_conf = Mock(return_value={})
        action.action()
        # Update
        c.get_function_conf = Mock(return_value={'foo': 'bar'})
        action.action()

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
        action = DeployAction(default_args())
        eq_(action._get_conf_diff(remote, local), ret)

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
        action = DeployAction(default_args())
        action._print_conf_diff(remote, local)


class SetAliasActionTestCase(TestCase):

    @patch('lamvery.actions.Client')
    def test_action(self, c):
        # No alias
        action = SetAliasAction(default_args())
        action.action()

        # Dry run
        args = default_args()
        args.alias = 'foo'
        action = SetAliasAction(args)
        action.action()

        # No dry run
        args = default_args()
        args.alias = 'foo'
        args.dry_run = False
        # New
        c.get_alias = Mock(return_value={})
        action = SetAliasAction(args)
        action.action()
        # Update
        c.get_alias.return_value = {'FunctionVersion': '1'}
        action = SetAliasAction(args)
        action.action()

    def test_print_alias_diff(self):
        action = SetAliasAction(default_args())
        action._print_alias_diff('name', {'FunctionVersion': 1}, 2)

    def test_get_alias_name(self):
        action = SetAliasAction(default_args())
        eq_(action._get_alias_name(), None)
        args = default_args()
        args.alias = 'foo'
        action = SetAliasAction(args)
        eq_(action._get_alias_name(), 'foo')

    def test_get_alias_version(self):
        action = SetAliasAction(default_args())
        eq_(action._get_alias_version(), '$LATEST')
        args = default_args()
        args.alias_version = '1'
        action = SetAliasAction(args)
        eq_(action._get_alias_version(), '1')

class EncryptActionTestCase(TestCase):

    def test_action(self):
        with patch('lamvery.actions.Client'):
            args = default_args()
            action = EncryptAction(args)
            action._config = Mock()
            action.action()
            args.store_secret = False
            action.action()

class DecryptActionTestCase(TestCase):

    def test_action(self):
        with patch('lamvery.actions.Client'):
            action = DecryptAction(default_args())
            action._config = Mock()
            action.action()
