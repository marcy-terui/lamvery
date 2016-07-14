# -*- coding: utf-8 -*-

from unittest import TestCase
from mock import Mock, patch

from lamvery.actions.encrypt_file import EncryptFileAction


def default_args():
    args = Mock()
    args.conf_file = '.lamvery.yml'
    args.path = 'requirements.txt'
    args.file = 'bar.txt'
    args.store = False
    return args


class EncryptActionTestCase(TestCase):

    def test_action(self):
        with patch('lamvery.actions.base.KmsClient'):
            args = default_args()
            action = EncryptFileAction(args)
            action._config = Mock()
            action.action()

            args.store = True
            action = EncryptFileAction(args)
            action._config.store_secret_file = Mock()
            action.action()
