# -*- coding: utf-8 -*-

from unittest import TestCase
from mock import Mock, patch

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
        with patch('lamvery.actions.base.LambdaClient') as c:
            m = Mock()
            m.invoke = Mock(return_value={'LogResult': base64.b64encode('foo')})
            c.return_value = m
            action = InvokeAction(default_args())
            action.action()

            args = default_args()
            args.json = '.lamvery.yml'
            action = InvokeAction(args)
            m.invoke = Mock(
                return_value={'FunctionError': 'unhandled', 'LogResult': base64.b64encode('foo')})
            c.return_value = m
            action._get_client = c
            action.action()
