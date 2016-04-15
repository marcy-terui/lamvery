# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import eq_
from mock import Mock

from lamvery.actions.api import (
    ApiAction,
    DEFAULT_MAPPING_TEMPLATE
)


def default_args():
    args = Mock()
    args.conf_file = '.lamvery.yml'
    args.dry_run = False
    args.no_integrate = False
    args.remove = False
    args.write_id = True
    args.stage = None
    return args


class ApiActionTestCase(TestCase):

    def test_get_stage_name(self):
        args = default_args()
        api = ApiAction(args)
        eq_(api.get_stage_name(), 'dev')

        args = default_args()
        args.stage = 'prod'
        api = ApiAction(args)
        eq_(api.get_stage_name(), 'prod')

    def test_get_cors(self):
        args = default_args()
        api = ApiAction(args)
        eq_(api.get_cors().get('origin'), "'*'")

    def test_action(self):
        args = default_args()
        api = ApiAction(args)
        api._config.save_api_id = Mock()
        api._get_client = Mock()
        api._apply_api = Mock(
            return_value={'id': 'foo', 'name': 'bar', 'description': 'baz'})
        api._deploy = Mock(
            return_value={'id': 'foo', 'apiSummary': 'bar', 'description': 'baz'})
        api._get_remote_configuration = Mock(return_value={})
        api.action()

    def test_add_permissions(self):
        args = default_args()
        api = ApiAction(args)
        api._get_client = Mock()
        api._add_permissions('foo', {'paths': {'/': {'get': {'bar': 'baz'}}}})

    def test_get_remote_configuration(self):
        args = default_args()
        api = ApiAction(args)
        m = Mock()
        m.get_export = Mock(return_value={'foo': 'bar'})
        eq_(api._get_remote_configuration(m, 'baz', 'qux'), {'foo': 'bar'})

    def test_integrate_aws(self):
        args = default_args()
        api = ApiAction(args)
        api._get_client = Mock()
        ret = api._integrate_aws(
            {'paths': {'/': {'get': {'responses': {'get': {'foo': 'bar'}}}}}, 'info': {}},
            'baz',
            {'methods': "'GET,OPTION'", 'headers': 'foo,bar', 'origin': "'*'"})
        eq_(
            ret['paths']['/']['get']['x-amazon-apigateway-integration']['requestTemplates'],
            {'application/json': DEFAULT_MAPPING_TEMPLATE})
        eq_(ret['basePath'], '/baz')

    def test_generate_method_cors(self):
        args = default_args()
        api = ApiAction(args)
        eq_(
            api._generate_method_cors({'origin': "'*'"}),
            {
                'method.response.header.Access-Control-Allow-Origin': "'*'"
            })

    def test_generate_option_cors(self):
        args = default_args()
        api = ApiAction(args)
        ret = api._generate_option_cors(
            {'methods': "'GET,OPTION'", 'headers': "'foo,bar'", 'origin': "'*'"})
        eq_(
            ret['x-amazon-apigateway-integration']['responses']['default']['responseParameters'],
            {
                'method.response.header.Access-Control-Allow-Methods': "'GET,OPTION'",
                'method.response.header.Access-Control-Allow-Headers': "'foo,bar'",
                'method.response.header.Access-Control-Allow-Origin': "'*'"
            })

    def test_apply_api(self):
        args = default_args()
        api = ApiAction(args)
        c = Mock()
        c.import_rest_api = Mock(return_value='import_rest_api')
        c.put_rest_api = Mock(return_value='put_rest_api')
        c.get_rest_api = Mock(return_value=None)
        eq_(api._apply_api(c, 'baz', {'foo': 'bar'}), 'import_rest_api')
        c.get_rest_api = Mock(return_value='baz')
        eq_(api._apply_api(c, 'baz', {'foo': 'bar'}), 'put_rest_api')

        args = default_args()
        args.remove = True
        api = ApiAction(args)
        c.get_rest_api = Mock(return_value=None)
        eq_(api._apply_api(c, 'baz', {'foo': 'bar'}), None)
        c.get_rest_api = Mock(return_value='baz')
        eq_(api._apply_api(c, 'baz', {'foo': 'bar'}), None)

    def test_print_apply_result(self):
        args = default_args()
        api = ApiAction(args)
        api._print_apply_result({
            'id': 'foo',
            'name': 'bar',
            'description': 'baz',
            'warnings': ['qux']})

    def test_deploy(self):
        args = default_args()
        api = ApiAction(args)
        c = Mock()
        c.create_deployment = Mock(return_value='foo')
        eq_(api._deploy(c, 'bar', 'baz'), 'foo')

    def test_print_deploy_result(self):
        args = default_args()
        api = ApiAction(args)
        api._print_deploy_result({
            'id': 'foo',
            'apiSummary': 'bar',
            'description': 'baz'})

    def test_print_conf_diff(self):
        args = default_args()
        api = ApiAction(args)
        api._print_conf_diff({'foo': 'bar'}, {'foo': 'baz'})
