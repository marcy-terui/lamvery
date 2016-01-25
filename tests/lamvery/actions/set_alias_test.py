# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import ok_, eq_, raises
from mock import Mock,MagicMock,patch

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
        args.version = '1'
        action = SetAliasAction(args)
        eq_(action._get_alias_version(), '1')
