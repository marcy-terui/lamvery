# -*- coding: utf-8 -*-

import botocore

from unittest import TestCase
from nose.tools import ok_, eq_
from mock import Mock
from lamvery.clients.events import EventsClient


class EventsClientTestCase(TestCase):

    def setUp(self):
        self.client = EventsClient(region='us-east-1')
        self.client._events = Mock()

    def test_get_rules_by_target(self):
        self.client._get_rule_names_by_tagert = Mock(return_value=['foo', 'bar'])
        self.client._events.describe_rule = Mock(return_value={'foo': 'bar'})
        eq_(self.client.get_rules_by_target('foo'), [{'foo': 'bar'}, {'foo': 'bar'}])

    def test_get_rule_names_by_tagert(self):
        ret1 = {'RuleNames': ['foo', 'bar'], 'NextToken': 'foo'}
        ret2 = {'RuleNames': ['baz', 'qux']}
        self.client._events.list_rule_names_by_target = Mock(side_effect=[ret1, ret2])
        eq_(self.client._get_rule_names_by_tagert('foo'), ['foo', 'bar', 'baz', 'qux'])

        self.client._events.list_rule_names_by_target = Mock(
            side_effect=botocore.exceptions.ClientError({'Error': {}}, 'bar'))
        eq_(self.client._get_rule_names_by_tagert('foo', 'bar'), [])

    def test_put_rule(self):
        rule = {
            'rule': 'foo',
            'description': 'bar',
            'pattern': 'baz',
            'schedule': 'qux'}
        ok_(self.client.put_rule(rule) != {})
        client = EventsClient(region='us-east-1', profile=None, dry_run=True)
        eq_(client.put_rule({'rule': 'foo'}), {})

    def test_put_targets(self):
        self.client.put_targets(
            'foo', [{'id': 'foo', 'input': 'bar', 'input_path': 'baz'}], 'baz')

    def test_get_targets_by_rule(self):
        ret1 = {'Targets': [{'foo': 'bar'}], 'NextToken': 'foo'}
        ret2 = {'Targets': [{'baz': 'qux'}]}
        self.client._events.list_targets_by_rule = Mock(side_effect=[ret1, ret2])
        eq_(self.client.get_targets_by_rule('foo'), [{'foo': 'bar'}, {'baz': 'qux'}])

        self.client._events.list_targets_by_rule = Mock(
            side_effect=botocore.exceptions.ClientError({'Error': {}}, 'bar'))
        eq_(self.client.get_targets_by_rule('foo', 'bar'), [])

    def test_remove_targets(self):
        self.client.remove_targets('foo', ['bar', 'baz'])

    def test_delete_rule(self):
        self.client.delete_rule('foo')
