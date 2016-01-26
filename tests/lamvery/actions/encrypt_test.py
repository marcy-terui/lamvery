# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import ok_, eq_, raises
from mock import Mock,MagicMock,patch

from lamvery.actions.encrypt import EncryptAction

def default_args():
    args = Mock()
    args.conf_file = '.lamvery.yml'
    args.text = 'foo'
    args.secret_name = 'bar'
    args.store = False
    return args

class EncryptActionTestCase(TestCase):

    def test_action(self):
        with patch('lamvery.actions.base.Client'):
            args = default_args()
            action = EncryptAction(args)
            action._config = Mock()
            action.action()
            args.store_secret = True
            action.action()
