# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import eq_
from mock import Mock, patch

from lamvery.actions.init import InitAction
import lamvery.actions.init


def default_args():
    args = Mock()
    args.conf_file = '.lamvery.yml'
    return args


class InitActionTestCase(TestCase):

    def test_action(self):
        action = InitAction(default_args())
        action._config = Mock()
        action._needs_write = Mock(return_value=True)
        action.action()

    def test_needs_write_conf(self):
        # New
        args = default_args()
        action = InitAction(args)
        eq_(action._needs_write('bar'), True)
        # Overwrite
        action = InitAction(default_args())

        with patch('sys.stdin') as r:
            # Overwrite yes
            r.readline = Mock(return_value='y')
            eq_(action._needs_write('.lamvery.yml'), True)
            # Overwrite no
            r.readline = Mock(return_value='n')
            eq_(action._needs_write('.lamvery.yml'), False)
