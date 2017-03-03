# -*- coding: utf-8 -*-

import os

from unittest import TestCase
from nose.tools import eq_
from mock import Mock
from lamvery.config import Config, represent_odict

DEFAULT_CONF = """
profile: default
region: us-east-1
configuration:
  runtime: python2.7
  name: test_lambda_function
  role: arn:aws:iam::000000000000:role/lambda_basic_execution
  handler: lambda_function.lambda_handler
  description: This is sample lambda function.
  timeout: 10
  memory_size: 128
  vpc_config:
    subnets:
    - subnet-xxxxxxxx
    security_groups:
    - sg-xxxxxxxx
  test_env: {{ env['PATH'] }}
event_file: .test.event.yml
secret_file: .test.secret.yml
exclude_file: .test.exclude.yml
api_file: .test.api.yml
"""

DEFAULT_EVENTS = """
- rule: foo
  description: This is a sample CloudWatchEvent
  schedule: rate(5 minutes)
"""

DEFAULT_SECRET = """
key_id: <key-id>
cipher_texts:
  foo: bar
secret_files:
  baz: qux
test_env: {{ env['PATH'] }}
"""

DEFAULT_EXCLUDE = """
- ^bar
"""

DEFAULT_API = """
api_id: myipugal74
stage: dev
cors:
  origin: '*'
  methods:
  - GET
  - OPTION
  headers:
  - Content-Type
  - X-Amz-Date
  - Authorization
  - X-Api-Key
configuration:
  swagger: '2.0'
  info:
    title: Sample API
  schemes:
  - https
  paths:
    /:
      get:
        produces:
        - application/json
        parameters:
        - name: sample
          in: query
          required: false
          type: string
        responses:
          '200':
            description: 200 response
            schema:
              $ref: '#/definitions/Sample'
  definitions:
    Sample:
      type: object
"""

NODE_CONF = DEFAULT_CONF.replace('python2.7', 'nodejs')
NODE43_CONF = DEFAULT_CONF.replace('python2.7', 'nodejs4.3')


class FunctionsTestCase(TestCase):

    def test_represent_odict(self):
        dumper = Mock()
        dumper.represent_mapping = Mock(return_value='test')
        eq_(represent_odict(dumper, {'foo': 'bar'}), 'test')


class ConfigTestCase(TestCase):

    def setUp(self):
        self.conf_file = '.test.lamvery.yml'
        self.event_file = '.test.event.yml'
        self.secret_file = '.test.secret.yml'
        self.exclude_file = '.test.exclude.yml'
        self.api_file = '.test.api.yml'
        open(self.conf_file, 'w').write(DEFAULT_CONF)
        open(self.event_file, 'w').write(DEFAULT_EVENTS)
        open(self.secret_file, 'w').write(DEFAULT_SECRET)
        open(self.exclude_file, 'w').write(DEFAULT_EXCLUDE)
        open(self.api_file, 'w').write(DEFAULT_API)

    def tearDown(self):
        os.remove(self.conf_file)
        os.remove(self.event_file)
        os.remove(self.secret_file)
        os.remove(self.exclude_file)
        os.remove(self.api_file)

    def test_load(self):
        config = Config(self.conf_file)
        eq_(config.load(self.conf_file).get('profile'), 'default')

    def test_load_conf(self):
        config = Config(self.conf_file)
        eq_(config.load_conf().get('profile'), 'default')

    def test_load_events(self):
        config = Config(self.conf_file)
        eq_(config.load_events().pop().get('rule'), 'foo')

    def test_get_event_file(self):
        config = Config(self.conf_file)
        eq_(config.get_event_file(), '.test.event.yml')

    def test_load_secret(self):
        config = Config(self.conf_file)
        eq_(config.load_secret().get('cipher_texts'), {'foo': 'bar'})

    def test_get_secret_file(self):
        config = Config(self.conf_file)
        eq_(config.get_secret_file(), '.test.secret.yml')

    def test_load_exclude(self):
        config = Config(self.conf_file)
        eq_(config.load_exclude().pop(), '^bar')

    def test_get_exclude_file(self):
        config = Config(self.conf_file)
        eq_(config.get_exclude_file(), '.test.exclude.yml')

    def test_get_runtime(self):
        config = Config(self.conf_file)
        eq_(config.get_runtime(), 'python2.7')

        open(self.conf_file, 'w').write(NODE_CONF)
        config = Config(self.conf_file)
        runtime = config.get_configuration().get('runtime')
        eq_(runtime, 'nodejs4.3')

        open(self.conf_file, 'w').write(NODE43_CONF)
        config = Config(self.conf_file)
        runtime = config.get_configuration().get('runtime')
        eq_(runtime, 'nodejs4.3')

    def test_get_handler(self):
        config = Config(self.conf_file)
        eq_(config.get_handler(), 'lambda_function.lambda_handler')

    def test_get_namespace(self):
        config = Config(self.conf_file)
        eq_(config.get_handler_namespace(), 'lambda_function')

    def test_get_handler_function(self):
        config = Config(self.conf_file)
        eq_(config.get_handler_function(), 'lambda_handler')

    def test_load_raw_secret(self):
        config = Config(self.conf_file)
        eq_(config.load_raw_secret().get('test_env'), "{{ env[$$PATH$$] }}")

    def test_escape(self):
        config = Config(self.conf_file)
        eq_(config.escape("{{ foo['bar'] }}"), "'{{ foo[$$bar$$] }}'")
        eq_(config.escape('{% foo["bar"] %}'), '\'{% foo["bar"] %}\'')

    def test_get_configuration(self):
        config = Config(self.conf_file)
        eq_(config.get_configuration().get('test_env'), os.environ.get('PATH'))

    def test_get_vpc_configuration(self):
        config = Config(self.conf_file)
        eq_(config.get_vpc_configuration().get('subnets'), ['subnet-xxxxxxxx'])
        config.get_configuration = Mock(return_value={})
        eq_(config.get_vpc_configuration().get('subnets'), [])

    def test_get_function_name(self):
        config = Config(self.conf_file)
        eq_(config.get_function_name(), 'test_lambda_function')
        config = Config('/foo/bar')
        eq_(config.get_function_name(), os.path.basename(os.getcwd()))

    def test_get_function_filename(self):
        config = Config(self.conf_file)
        eq_(config.get_function_filename(), 'lambda_function.py')

        open(self.conf_file, 'w').write(NODE_CONF)
        config = Config(self.conf_file)
        eq_(config.get_function_filename(), 'lambda_function.js')

        open(self.conf_file, 'w').write(NODE43_CONF)
        config = Config(self.conf_file)
        eq_(config.get_function_filename(), 'lambda_function.js')

    def test_get_archive_name(self):
        config = Config(self.conf_file)
        eq_(config.get_archive_name(), 'test_lambda_function.zip')

    def test_get_region(self):
        config = Config(self.conf_file)
        eq_(config.get_region(), 'us-east-1')
        config = Config('/foo/bar')
        eq_(config.get_region(), None)

    def test_get_profile(self):
        config = Config(self.conf_file)
        eq_(config.get_profile(), 'default')

    def test_get_exclude(self):
        config = Config(self.conf_file)
        eq_(config.get_exclude(), ['^bar'])

    def test_get_default(self):
        config = Config(self.conf_file)
        runtime = config.get_default().get('configuration').get('runtime')
        eq_(runtime, 'python2.7')
        subnets = config.get_default().get('configuration').get('vpc_config').get('subnets')
        eq_(subnets, ['subnet-xxxxxxxx'])

    def test_get_default_events(self):
        config = Config(self.conf_file)
        eq_(
            config.get_default_events().get('rules').pop().get('name'),
            'sample-rule-name')

    def test_get_default_secret(self):
        config = Config(self.conf_file)
        eq_(config.get_default_secret().get('key_id'), '<key-id>')

    def test_get_default_exclude(self):
        config = Config(self.conf_file)
        eq_(config.get_default_exclude().pop(), '^\\.test\\.exclude\\.yml$')

    def test_get_default_hook(self):
        config = Config(self.conf_file)
        eq_(config.get_default_hook().get('build').get('pre'), [])
        eq_(config.get_default_hook().get('build').get('post'), [])

    def test_get_default_api(self):
        config = Config(self.conf_file)
        eq_(config.get_default_api().get('api_id'), '<your-rest-api-id>')
        eq_(
            config.get_default_api().get('configuration').get('info'),
            {'title': 'Sample API'})

    def test_get_secret(self):
        config = Config(self.conf_file)
        key = config.get_secret().get('key_id')
        eq_(key, '<key-id>')

    def test_generate_lambda_secret(self):
        config = Config(self.conf_file)
        secret = config.generate_lambda_secret()
        eq_(secret, {
            'region': 'us-east-1',
            'cipher_texts': {
                'foo': 'bar'
            },
            'secret_files': {
                'baz': 'qux'
            }
        })

    def test_store_secret(self):
        config = Config(self.conf_file)
        config.store_secret('foo', 'bar')
        eq_(config.get_secret().get('key_id'), '<key-id>')
        eq_(config.get_secret().get('cipher_texts').get('foo'), 'bar')

    def test_store_secret_file(self):
        config = Config(self.conf_file)
        config.store_secret_file('baz', 'qux')
        eq_(config.get_secret().get('key_id'), '<key-id>')
        eq_(config.get_secret().get('secret_files').get('baz'), 'qux')

    def test_save_api_id(self):
        config = Config(self.conf_file)
        config.save_api_id('foo')
        eq_(config.get_api_id(), 'foo')
        eq_(config.get_api_stage(), 'dev')

    def test_get_events(self):
        config = Config(self.conf_file)
        eq_(config.get_events().get('rules').pop().get('schedule'), 'rate(5 minutes)')
        config.load_events = Mock(return_value=None)
        eq_(config.get_events(), {'rules': []})
        config.load_events = Mock(return_value=[{'rule': 'foo'}])
        eq_(config.get_events(), {'rules': [{'rule': 'foo', 'name': 'foo'}]})
