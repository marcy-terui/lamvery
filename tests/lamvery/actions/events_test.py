# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import ok_, eq_, raises
from mock import Mock,MagicMock,patch

from lamvery.actions.events import EventsAction

def default_args():
    args = Mock()
    args.conf_file = '.lamvery.yml'
    args.keep_empty_events = False
    return args

class EventsActionTestCase(TestCase):

    @raises(Exception)
    def test_action_function_not_exists(self):
        with patch('lamvery.actions.base.Client') as c:
            c.get_function_conf = Mock(return_value={})
            action = EventsAction(default_args())
            action.get_client = Mock(return_value=c)
            actin.action()

    def test_action(self):
        with patch('lamvery.actions.base.Client') as c:
            c.get_function_conf = Mock(return_value={'FunctionArn': 'foo'})
            action = EventsAction(default_args())
            action._put_rules = Mock()
            action._put_target = Mock()
            action._clean = Mock()
            action.get_client = Mock(return_value=c)
            action.action()

    def test_put_rules(self):
        with patch('lamvery.actions.base.Client') as c:
            c.get_function_conf = Mock(return_value={'FunctionArn': 'foo'})
            action = EventsAction(default_args())
            action.get_client = Mock(return_value=c)
            action._put_rules(
                remote=[{'Name': 'bar'}],
                local=[{'rule': 'foo'}, {'rule': 'bar'}],
                function='baz')

    def test_convert_state(self):
        action = EventsAction(default_args())
        eq_(action._convert_state(True), 'DISABLED')
        eq_(action._convert_state(False), 'ENABLED')

    def test_search_rule(self):
        action = EventsAction(default_args())
        eq_(action._search_rule([{'Name': 'foo'}, {'rule': 'bar'}], 'bar'), {'rule': 'bar'})
        eq_(action._search_rule([{'Name': 'foo'}, {'rule': 'bar'}], 'baz'), {})

    def test_exist_rule(self):
        action = EventsAction(default_args())
        eq_(action._exist_rule([{'Name': 'foo'}, {'rule': 'bar'}], 'bar'), True)
        eq_(action._exist_rule([{'Name': 'foo'}, {'rule': 'bar'}], 'baz'), False)

    def test_exist_target(self):
        action = EventsAction(default_args())
        eq_(action._exist_target([{'Id': 'foo'}, {'id': 'bar'}], 'bar'), True)
        eq_(action._exist_target([{'Id': 'foo'}, {'id': 'bar'}], 'baz'), False)

    def test_put_targets(self):
        with patch('lamvery.actions.base.Client') as c:
            c.get_targets_by_rule = Mock(return_value=[{'Id': 'baz'}])
            action = EventsAction(default_args())
            local = [
                {'rule': 'foo', 'targets': [{'id': 'baz'}]},
                {'rule': 'bar', 'targets': [{'id': 'qux'}]}
            ]
            action.get_client = Mock(return_value=c)
            action._put_targets(local=local, arn='baz')

    def test_clean(self):
        with patch('lamvery.actions.base.Client') as c:
            c.get_targets_by_rule = Mock(return_value=[{'Id': 'foo','Arn': 'baz'}])
            action = EventsAction(default_args())
            action.get_client = Mock(return_value=c)
            action._clean(
                remote=[{'Name': 'bar'}],
                local=[{'rule': 'foo', 'targets': []}, {'rule': 'bar', 'targets': []}],
                arn='baz',
                function='qux')
            action._clean(
                remote=[{'Name': 'bar'}],
                local=[{'rule': 'foo', 'targets': []}],
                arn='baz',
                function='qux')
