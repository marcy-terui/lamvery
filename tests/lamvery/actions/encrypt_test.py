# -*- coding: utf-8 -*-

from unittest import TestCase
from mock import Mock, patch

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

            args.store = True
            action = EncryptAction(args)
            action._config.store_secret = Mock()
            action.action()
