# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import eq_, raises
from mock import Mock

from lamvery.actions.base import BaseAction
from lamvery.actions.configure import CONF_DIFF_KEYS


def default_args():
    args = Mock()
    args.conf_file = '.lamvery.yml'
    args.dry_run = True
    args.alias = None
    return args


class TestAction(BaseAction):
    def action(self):
        pass


class BaseActionTestCase(TestCase):

    @raises(TypeError)
    def test_action(self):
        BaseAction(default_args())

    def test_get_client(self):
        TestAction(default_args())._get_client(Mock)

    def test_get_diff(self):
        remote = {
            'Runtime': 'python2.7',
            'Role': 'foo',
            'Handler': 'bar',
        }
        local = {
            'runtime': 'python2.7',
            'role': 'bar',
        }
        ret = {
            'runtime': None,
            'role': ('foo', 'bar',),
            'handler': ('bar', None,),
            'description': None,
            'timeout': None,
            'memory_size': None,
        }
        action = TestAction(default_args())
        eq_(action._get_diff(remote, local, CONF_DIFF_KEYS), ret)

    def test_print_diff(self):
        remote = {
            'Runtime': 'python2.7',
            'Role': 'foo',
            'Handler': 'bar',
        }
        local = {
            'runtime': 'python2.7',
            'role': 'bar',
        }
        action = TestAction(default_args())
        action._print_diff('test', remote, local, CONF_DIFF_KEYS)

    def test_get_alias_name(self):
        action = TestAction(default_args())
        eq_(action.get_alias_name(), 'test')
        args = default_args()
        args.alias = 'foo'
        action = TestAction(args)
        eq_(action.get_alias_name(), 'foo')
