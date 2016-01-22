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
    args.keep_empty_events = False
    return args

class TestAction(BaseAction):
    def action(self):
        pass

class BaseActionTestCase(TestCase):

    @raises(TypeError)
    def test_action(self):
        BaseAction(default_args())

    def test_get_client(self):
        TestAction(default_args()).get_client()

    def test_get_diff(self):
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
        action = TestAction(default_args())
        eq_(action._get_diff(remote, local, CONF_DIFF_KEYS), ret)

    def test_print_diff(self):
        remote = {
            'Runtime': 'python2.7',
            'Role': 'foo',
            'Handler': 'bar',
        }
        local = {
            'runtime': 'python2.7',
            'role': 'bar',
        }
        action = TestAction(default_args())
        action._print_diff('test', remote, local, CONF_DIFF_KEYS)

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

class ConfigureActionTestCase(TestCase):

    @raises(Exception)
    def test_action_not_exists(self):
        with patch('lamvery.actions.Client') as c:
            action = ConfigureAction(default_args())
            action._print_conf_diff = Mock()
            c.get_function_conf = Mock(return_value={})
            action.action()

    def test_action(self):
        c = Mock()
        c.get_function_conf = Mock(return_value={'foo': 'bar'})

        # Dry run
        action = ConfigureAction(default_args())
        action.get_client = Mock(return_value=c)
        action._print_conf_diff = Mock()
        action.action()

        # No dry run
        args = default_args()
        args.dry_run = False
        action = ConfigureAction(args)
        action.get_client = Mock(return_value=c)
        action._print_conf_diff = Mock()
        action.action()

class DeployActionTestCase(TestCase):

    @patch('lamvery.actions.SetAliasAction')
    @patch('lamvery.actions.Client')
    def test_action(self, a, c):
        # Dry run
        action = DeployAction(default_args())
        action._print_conf_diff = Mock()
        action._print_capacity = Mock()
        action.action()

        # No dry run
        args = default_args()
        args.dry_run = False
        action = DeployAction(args)
        action._print_conf_diff = Mock()
        action._print_capacity = Mock()
        # New
        c.get_function_conf = Mock(return_value={})
        action.get_client = Mock(return_value=c)
        action.action()
        # Update
        c.get_function_conf = Mock(return_value={'foo': 'bar'})
        action.get_client = Mock(return_value=c)
        action.action()

    def test_print_capacity(self):
        action = DeployAction(default_args())
        action._print_capacity(1000000, 200000)

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

class EventsActionTestCase(TestCase):

    @raises(Exception)
    def test_action_function_not_exists(self):
        with patch('lamvery.actions.Client') as c:
            c.get_function_conf = Mock(return_value={})
            action = EventsAction(default_args())
            actin.action()

    def test_action(self):
        with patch('lamvery.actions.Client') as c:
            c.get_function_conf = Mock(return_value={'FunctionArn': 'foo'})
            action = EventsAction(default_args())
            action._put_rules = Mock()
            action._put_target = Mock()
            action._clean = Mock()
            action.action()

    def test_put_rules(self):
        with patch('lamvery.actions.Client') as c:
            c.get_function_conf = Mock(return_value={'FunctionArn': 'foo'})
            action = EventsAction(default_args())
            action._put_rules(remote=[{'Name': 'bar'}], local=[{'rule': 'foo'}, {'rule': 'bar'}])

    def test_convert_state(self):
        action = EventsAction(default_args())
        eq_(action._convert_state(True), 'DISABLED')
        eq_(action._convert_state(False), 'ENABLED')

    def test_search_rule(self):
        action = EventsAction(default_args())
        eq_(action._search_rule([{'Name': 'foo'}, {'rule': 'bar'}], 'bar'), {'rule': 'bar'})
        eq_(action._search_rule([{'Name': 'foo'}, {'rule': 'bar'}], 'baz'), {})

    def test_exist_rule(self):
        action = EventsAction(default_args())
        eq_(action._exist_rule([{'Name': 'foo'}, {'rule': 'bar'}], 'bar'), True)
        eq_(action._exist_rule([{'Name': 'foo'}, {'rule': 'bar'}], 'baz'), False)

    def test_put_targets(self):
        with patch('lamvery.actions.Client') as c:
            action = EventsAction(default_args())
            local = [
                {'rule': 'foo', 'targets': [{'id': 'baz'}]},
                {'rule': 'bar', 'targets': [{'id': 'qux'}]}
            ]
            action._put_targets(local=local, arn='baz')

    def test_clean(self):
        with patch('lamvery.actions.Client') as c:
            c.get_targets_by_rule = Mock(return_value=[{'Arn': 'baz'}])
            action = EventsAction(default_args())
            action._clean(remote=[{'Name': 'bar'}], local=[{'rule': 'foo'}, {'rule': 'bar'}], arn='baz')
