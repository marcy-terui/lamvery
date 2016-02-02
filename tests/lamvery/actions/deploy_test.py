# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import eq_
from mock import Mock, patch

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
    def test_action(self, a):
        # Dry run
        with patch('lamvery.actions.base.Client') as c:
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
        with patch('lamvery.actions.base.Client') as c:
            action._enable_versioning = Mock(return_value=False)
            c.get_function_conf = Mock(return_value={})
            action.get_client = Mock(return_value=c)
            action.action()
        # Update
        with patch('lamvery.actions.base.Client') as c:
            action._enable_versioning = Mock(return_value=False)
            c.get_function_conf = Mock(return_value={'CodeSize': 100})
            action.get_client = Mock(return_value=c)
            action.action()
        # Update (versioning)
        with patch('lamvery.actions.base.Client') as c:
            action._enable_versioning = Mock(return_value=True)
            c.get_function_conf = Mock(return_value={'CodeSize': 100})
            action.get_client = Mock(return_value=c)
            action.action()

        # Single File
        with patch('lamvery.actions.base.Client') as c:
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

    def test_enable_versioning(self):
        args = default_args()
        action = DeployAction(args)
        eq_(action._enable_versioning(), True)

        args.publish = False
        action = DeployAction(args)
        eq_(action._enable_versioning(), True)
