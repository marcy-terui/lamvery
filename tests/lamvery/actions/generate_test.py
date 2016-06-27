# -*- coding: utf-8 -*-

import os

from unittest import TestCase
from nose.tools import eq_, raises
from mock import Mock, patch

from lamvery.actions.generate import GenerateAction


def default_args():
    args = Mock()
    args.conf_file = '.lamvery.yml'
    args.kind = 'function'
    return args


class GenerateActionTestCase(TestCase):

    def tearDown(self):
        for suffix in ['py', 'js']:
            filename = 'namespace.{}'.format(suffix)
            if os.path.exists(filename):
                os.remove(filename)

    def test_action(self):
        with patch('lamvery.actions.init.confirm_overwrite') as c:
            c.return_value = True
            action = GenerateAction(default_args())
            action._config = Mock()
            action._config.get_runtime = Mock(return_value='python2.7')
            action._config.get_handler_namespace = Mock(return_value='namespace')
            action._config.get_handler_function = Mock(return_value='function')
            action.action()
            eq_(open('namespace.py', 'r').read(), """import lamvery

def function(event, context):
    # Use environment variables
    # lamvery.env.load()
    # print(os.environ['FOO'])

    # Use KMS encryption
    # print(lamvery.secret.get('foo'))

    print('This is a skeleton function.')
""")

    @raises(Exception)
    def test_action_invalid_kind(self):
        args = default_args()
        args.kind = 'foo'
        action = GenerateAction(args)
        action._config = Mock()
        action._config.get_runtime = Mock(return_value='python2.7')
        action._config.get_handler_namespace = Mock(return_value='namespace')
        action._config.get_handler_function = Mock(return_value='function')
        action.action()

    @raises(Exception)
    def test_action_invalid_runtime(self):
        action = GenerateAction(default_args())
        action._config = Mock()
        action._config.get_runtime('foo')
        action._config.get_handler_namespace = Mock(return_value='namespace')
        action._config.get_handler_function = Mock(return_value='function')
        action.action()
