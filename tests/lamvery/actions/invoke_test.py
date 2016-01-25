# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import ok_, eq_, raises
from mock import Mock,MagicMock,patch

from lamvery.actions.invoke import InvokeAction

import base64

def default_args():
    args = Mock()
    args.conf_file = '.lamvery.yml'
    args.alias = 'foo'
    args.version = '1'
    args.json = '{"foo": "bar"}'
    return args

class InvokeActionTestCase(TestCase):

    def test_action(self):
        with patch('lamvery.actions.base.Client') as c:
            c.invoke = Mock(return_value={'LogResult': base64.b64encode('foo')})
            action = InvokeAction(default_args())
            action.action()
            args = default_args()
            args.json = '.lamvery.yml'
            action = InvokeAction(args)
            c.invoke = Mock(
                return_value={'FunctionError': 'unhandled', 'LogResult': base64.b64encode('foo')})
            action.action()
