# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import ok_, eq_, raises
from mock import Mock,MagicMock,patch

from lamvery.actions.decrypt import DecryptAction

def default_args():
    args = Mock()
    args.conf_file = '.lamvery.yml'
    args.dry_run = True
    args.secret_name = 'bar'
    return args

class DecryptActionTestCase(TestCase):

    def test_action(self):
        with patch('lamvery.actions.base.Client'):
            action = DecryptAction(default_args())
            action._config = Mock()
            action.action()
