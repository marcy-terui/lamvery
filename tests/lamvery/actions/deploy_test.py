# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import ok_, eq_, raises
from mock import Mock,MagicMock,patch

from lamvery.actions.deploy import DeployAction

def default_args():
    args = Mock()
    args.conf_file = '.lamvery.yml'
    args.dry_run = True
    args.publish = True
    args.no_libs = False
    args.single_file = False

    return args


class DeployActionTestCase(TestCase):

    @patch('lamvery.actions.deploy.SetAliasAction')
    @patch('lamvery.actions.base.Client')
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
        args.publish = False
        c.get_function_conf = Mock(return_value={})
        action.get_client = Mock(return_value=c)
        action.action()
        # Update
        args.publish = True
        c.get_function_conf = Mock(return_value={'foo': 'bar'})
        action.get_client = Mock(return_value=c)
        action.action()

        # Single File
        args = default_args()
        args.single_file = True
        action = DeployAction(args)
        action._print_conf_diff = Mock()
        action._print_capacity = Mock()
        action.action()

    def test_print_capacity(self):
        action = DeployAction(default_args())
        action._print_capacity(1000000, 200000)
        action._print_capacity(1000000, -200)
