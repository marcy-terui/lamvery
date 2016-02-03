# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import raises
from mock import Mock, patch

from lamvery.actions.configure import ConfigureAction


def default_args():
    args = Mock()
    args.conf_file = '.lamvery.yml'
    args.dry_run = True
    return args


class ConfigureActionTestCase(TestCase):

    @raises(Exception)
    def test_action_not_exists(self):
        with patch('lamvery.actions.base.LambdaClient') as c:
            action = ConfigureAction(default_args())
            action._print_conf_diff = Mock()
            c.get_function_conf = Mock(return_value={})
            action.action()

    def test_action(self):
        c = Mock()
        c.get_function_conf = Mock(return_value={'foo': 'bar'})

        # Dry run
        action = ConfigureAction(default_args())
        action._get_client = Mock(return_value=c)
        action._print_conf_diff = Mock()
        action.action()

        # No dry run
        args = default_args()
        args.dry_run = False
        action = ConfigureAction(args)
        action._get_client = Mock(return_value=c)
        action._print_conf_diff = Mock()
        action.action()
