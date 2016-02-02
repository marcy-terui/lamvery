# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import eq_, raises
from mock import Mock, patch

from lamvery.actions.set_alias import SetAliasAction


def default_args():
    args = Mock()
    args.conf_file = '.lamvery.yml'
    args.dry_run = True
    args.publish = True
    args.alias = None
    args.version = None
    return args


class SetAliasActionTestCase(TestCase):

    @patch('lamvery.actions.base.Client')
    @raises(Exception)
    def test_action_not_exists(self, c):
        action = SetAliasAction(default_args())
        action.get_alias_name = Mock(return_value=None)
        action.action()

    @patch('lamvery.actions.base.Client')
    def test_action(self, c):

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
        with patch('lamvery.actions.base.Client') as c:
            c.get_alias = Mock(return_value={})
            action = SetAliasAction(args)
            action.action()

        # Update
        with patch('lamvery.actions.base.Client') as c:
            c.get_alias = Mock(return_value={'FunctionVersion': '1'})
            action = SetAliasAction(args)
            action.action()

    def test_print_alias_diff(self):
        action = SetAliasAction(default_args())
        action._print_alias_diff('name', {'FunctionVersion': 1}, 2)

    def test_get_alias_name(self):
        action = SetAliasAction(default_args())
        eq_(action.get_alias_name(), 'test')
        args = default_args()
        args.alias = 'foo'
        action = SetAliasAction(args)
        eq_(action.get_alias_name(), 'foo')

    def test_get_version(self):
        action = SetAliasAction(default_args())
        eq_(action.get_version(), '$LATEST')
        args = default_args()
        args.version = '1'
        action = SetAliasAction(args)
        eq_(action.get_version(), '1')
