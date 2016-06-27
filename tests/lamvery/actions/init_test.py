# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import eq_
from mock import Mock, patch

from lamvery.actions.init import InitAction


def default_args():
    args = Mock()
    args.conf_file = '.lamvery.yml'
    return args


class InitActionTestCase(TestCase):

    def test_action(self):
        with patch('lamvery.actions.init.confirm_overwrite') as c:
            c.return_value = True
            action = InitAction(default_args())
            action._config = Mock()
            action.action()
