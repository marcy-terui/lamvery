# -*- coding: utf-8 -*-

import botocore

from unittest import TestCase
from nose.tools import eq_
from mock import Mock
from lamvery.clients.function import LambdaClient

TEST_CONF = {
    'runtime': 'python2.7',
    'name': 'test_lambda_function',
    'role': 'arn:aws:iam::000000000000:role/lambda_basic_execution',
    'handler': 'lambda_function.lambda_handler',
    'description': 'This is sample lambda function.',
    'timeout': 10,
    'memory_size': 128,
    'vpc_config': {
        'subnets': ['subnet-xxxxxxxx'],
        'security_groups': ['sg-xxxxxxxx']
    }
}


class LambdaClientTestCase(TestCase):

    def setUp(self):
        self.client = LambdaClient(region='us-east-1')
        self.client._lambda = Mock()

    def test_get_function_conf(self):
        self.client._lambda.get_function = Mock(
            return_value={'Configuration': 'foo'})
        eq_(self.client.get_function_conf('test'), 'foo')
        self.client._lambda.get_function = Mock(
            side_effect=botocore.exceptions.ClientError({'Error': {}}, 'bar'))
        eq_(self.client.get_function_conf('test'), {})

    def test_create_function(self):
        self.client.create_function(Mock(), TEST_CONF, True)

    def test_update_function_code(self):
        self.client._lambda.update_function_code = Mock(return_value={'Version': '$LATEST'})
        eq_(self.client.update_function_code(Mock(), TEST_CONF, True), '$LATEST')

        self.client._dry_run = True
        eq_(self.client.update_function_code(Mock(), TEST_CONF, True), None)

    def test_update_function_conf(self):
        self.client.update_function_conf(TEST_CONF)

    def test_get_alias(self):
        self.client._lambda.get_alias = Mock(return_value='foo')
        eq_(self.client.get_alias('function', 'alias'), 'foo')
        self.client._lambda.get_alias = Mock(
            side_effect=botocore.exceptions.ClientError({'Error': {}}, 'bar'))
        eq_(self.client.get_alias('function', 'alias'), {})

    def test_create_alias(self):
        self.client.create_alias('function', 'alias', 'version')

    def test_update_alias(self):
        self.client.update_alias('function', 'alias', 'version')

    def test_calculate_capacity(self):
        ret1 = {
            'Functions': [{'FunctionName': 'foo'}, {'FunctionName': 'bar'}], 'NextMarker': 'foo'}
        ret2 = {
            'Functions': [{'FunctionName': 'foo'}, {'FunctionName': 'bar'}]}
        self.client._lambda.list_functions = Mock(side_effect=[ret1, ret2])
        self.client._calculate_versions_capacity = Mock(return_value=10)
        eq_(self.client.calculate_capacity(), 40)

    def test_calculate_versions_capacity(self):
        ret1 = {'Versions': [{'CodeSize': 20}, {'CodeSize': 20}], 'NextMarker': 'foo'}
        ret2 = {'Versions': [{'CodeSize': 20}, {'CodeSize': 20}]}
        self.client._lambda.list_versions_by_function = Mock(
            side_effect=[ret1, ret2])
        eq_(self.client._calculate_versions_capacity('foo'), 80)

    def test_add_permission(self):
        self.client.add_permission('foo', 'bar', 'baz')
        self.client._lambda.add_permission = Mock(
            side_effect=botocore.exceptions.ClientError({'Error': {}}, 'bar'))
        self.client.add_permission('foo', 'bar', 'baz')

    def test_remove_permission(self):
        self.client.remove_permission('foo', 'bar')

    def test_invoke(self):
        self.client.invoke('foo', 'bar', 'baz')

    def test_get_previous_version(self):
        self.client.get_alias = Mock(return_value={'FunctionVersion': 'foo'})
        eq_(self.client.get_previous_version('foo', 'bar'), 'foo')

    def test_generate_statement_id(self):
        self.client._generate_statement_id('foo', 'bar')
