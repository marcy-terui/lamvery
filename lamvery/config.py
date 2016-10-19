# -*- coding: utf-8 -*-

import yaml
import os
import re

from collections import OrderedDict
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from lamvery.log import get_logger

RUNTIME_PY_27 = 'python2.7'
RUNTIME_NODE_JS = 'nodejs'

RUNTIME_AND_EXTENSION = {
    RUNTIME_PY_27: 'py',
    RUNTIME_NODE_JS: 'js'
}


def represent_odict(dumper, instance):
    return dumper.represent_mapping(u'tag:yaml.org,2002:map', instance.items())

yaml.add_representer(OrderedDict, represent_odict)
yaml.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    lambda loader, node: OrderedDict(loader.construct_pairs(node)))


class Config:

    def __init__(self, conf_file):
        self._file = conf_file
        self._template_env = Environment(loader=FileSystemLoader('./', encoding='utf8'))

    def load(self, file, default={}):
        try:
            tmpl = self._template_env.get_template(file)
            return yaml.load(tmpl.render({'env': os.environ}))
        except TemplateNotFound:
            get_logger(__name__).warn(
                'Configuration file "{}" does not exist.'.format(file))
            return default

    def load_conf(self):
        return self.load(self._file)

    def load_events(self):
        return self.load(self.get_event_file())

    def get_event_file(self):
        return self.load_conf().get('event_file', '.lamvery.event.yml')

    def load_secret(self):
        return self.load(self.get_secret_file())

    def get_secret_file(self):
        return self.load_conf().get('secret_file', '.lamvery.secret.yml')

    def load_exclude(self):
        return self.load(self.get_exclude_file(), [])

    def get_exclude_file(self):
        return self.load_conf().get('exclude_file', '.lamvery.exclude.yml')

    def load_hook(self):
        return self.load(self.get_hook_file())

    def get_hook_file(self):
        return self.load_conf().get('hook_file', '.lamvery.hook.yml')

    def load_api(self):
        return self.load(self.get_api_file())

    def get_api_file(self):
        return self.load_conf().get('api_file', '.lamvery.api.yml')

    def load_raw(self, file_name):
        txt = open(file_name, 'r').read()
        return yaml.load(self.escape(txt))

    def load_raw_secret(self):
        return self.load_raw(self.get_secret_file())

    def load_raw_api(self):
        return self.load_raw(self.get_api_file())

    def escape(self, txt):
        txt = txt.replace("'", "$$")
        txt = txt.replace(
            self._template_env.variable_start_string,
            "'" + self._template_env.variable_start_string)
        txt = txt.replace(
            self._template_env.block_start_string,
            "'" + self._template_env.block_start_string)
        txt = txt.replace(
            self._template_env.variable_end_string,
            self._template_env.variable_end_string + "'")
        txt = txt.replace(
            self._template_env.block_end_string,
            self._template_env.block_end_string + "'")
        return txt

    def unescape(self, txt):
        txt = txt.replace("$$", "'")
        txt = txt.replace(
            "'" + self._template_env.variable_start_string,
            self._template_env.variable_start_string)
        txt = txt.replace(
            "'" + self._template_env.block_start_string,
            self._template_env.block_start_string)
        txt = txt.replace(
            self._template_env.variable_end_string + "'",
            self._template_env.variable_end_string)
        txt = txt.replace(
            self._template_env.block_end_string + "'",
            self._template_env.block_end_string)
        return txt

    def get_configuration(self):
        return self.load_conf().get('configuration')

    def get_vpc_configuration(self):
        vpc_config = self.get_configuration().get('vpc_config')

        if vpc_config is None:
            vpc_config = {}

        return {
            'subnets': vpc_config.get('subnets', []),
            'security_groups': vpc_config.get('security_groups', [])
        }

    def get_secret(self):
        return self.load_secret()

    def get_events(self):
        events = self.load_events()
        if events is None:
            return {'rules': []}

        if isinstance(events, list):
            rules = []
            for e in events:
                e['name'] = e['rule']
                rules.append(e)

            return {'rules': rules}

        if events.get('rules') is None:
            return {'rules': []}

        return events

    def get_default_alias(self):
        return self.load_conf().get('default_alias')

    def enable_versioning(self):
        return bool(self.load_conf().get('versioning'))

    def generate_lambda_secret(self):
        return {
            'region': self.get_region(),
            'cipher_texts': self.get_secret().get('cipher_texts'),
            'secret_files': self.get_secret().get('secret_files')
        }

    def get_function_name(self):
        if os.path.exists(self._file):
            return self.get_configuration().get('name')
        else:
            dirname = os.path.basename(os.getcwd())
            if dirname == '':
                return 'sample'
            return dirname

    def get_function_filename(self):
        ext = RUNTIME_AND_EXTENSION.get(self.get_runtime(), "py")
        return '{}.{}'.format(
            self.get_configuration().get('handler').split('.')[0], ext)

    def get_runtime(self):
        return self.get_configuration().get('runtime')

    def get_handler(self):
        return self.get_configuration().get('handler')

    def get_handler_namespace(self):
        return self.get_handler().split('.')[0]

    def get_handler_function(self):
        return self.get_handler().split('.')[1]

    def get_archive_name(self):
        return '{}.zip'.format(self.get_function_name())

    def get_region(self):
        if os.path.exists(self._file):
            return self.load_conf().get('region')
        else:
            return None

    def get_profile(self):
        return self.load_conf().get('profile')

    def get_exclude(self):
        exclude = self.load_exclude()
        if exclude is None:
            return []
        return exclude

    def get_build_hooks(self):
        return self.load_hook().get('build', {})

    def get_api_id(self):
        return self.load_api().get('api_id', None)

    def get_api_configuration(self):
        return self.load_api().get('configuration', {})

    def get_api_stage(self):
        return self.load_api().get('stage')

    def get_api_cors(self):
        return self.load_api().get('cors')

    def is_clean_build(self):
        return self.load_conf().get('clean_build', False)

    def get_default(self):
        init_vpc = OrderedDict()
        init_vpc['subnets'] = ['subnet-xxxxxxxx']
        init_vpc['security_groups'] = ['sg-xxxxxxxx']

        init_config = OrderedDict()
        init_config['name'] = self.get_function_name()
        init_config['runtime'] = RUNTIME_PY_27
        init_config['role'] = 'arn:aws:iam::<account-number>:role/<role>'
        init_config['handler'] = 'lambda_function.lambda_handler'
        init_config['description'] = 'This is a sample lambda function.'
        init_config['timeout'] = 10
        init_config['memory_size'] = 128
        init_config['vpc_config'] = init_vpc

        init_yaml = OrderedDict()
        init_yaml['profile'] = None
        init_yaml['region'] = 'us-east-1'
        init_yaml['versioning'] = False
        init_yaml['default_alias'] = None
        init_yaml['clean_build'] = False
        init_yaml['configuration'] = init_config

        return init_yaml

    def get_default_events(self):
        targets = [
            OrderedDict([
                ('id', '<unique-target-id>',),
                ('input', {'this': [{'is': 'a'}, {'sample': 'input'}]},),
                ('input_path', 'json.path.format',)])]
        event = OrderedDict()
        event['name'] = 'sample-rule-name'
        event['description'] = 'This is a sample CloudWatchEvent'
        event['schedule'] = 'rate(5 minutes)'
        event['targets'] = targets
        init_events = {'rules': [event]}

        return init_events

    def get_default_secret(self):
        init_secret = OrderedDict()
        init_secret['key_id'] = '<key-id>'
        init_secret['cipher_texts'] = OrderedDict()
        init_secret['secret_files'] = OrderedDict()

        return init_secret

    def get_default_exclude(self):
        return [
            '^{}$'.format(re.escape(self._file)),
            '^{}$'.format(re.escape(self.get_api_file())),
            '^{}$'.format(re.escape(self.get_hook_file())),
            '^{}$'.format(re.escape(self.get_event_file())),
            '^{}$'.format(re.escape(self.get_secret_file())),
            '^{}$'.format(re.escape(self.get_exclude_file()))]

    def get_default_hook(self):
        init_hook = OrderedDict()
        init_hook['build'] = OrderedDict()
        init_hook['build']['pre'] = []
        init_hook['build']['post'] = []

        return init_hook

    def get_default_api(self):
        init_api = OrderedDict()
        init_api['api_id'] = '<your-rest-api-id>'
        init_api['stage'] = 'dev'
        init_api['cors'] = OrderedDict([
            ('origin', '*',),
            ('methods', ['GET', 'OPTION'],),
            ('headers', ['Content-Type', 'X-Amz-Date', 'Authorization', 'X-Api-Key'],),
        ])
        init_api['configuration'] = OrderedDict([
            ('swagger', '2.0',),
            ('info', OrderedDict([
                ('title', 'Sample API',),
            ]),),
            ('schemes', ['https'],),
            ('paths', OrderedDict([
                ('/', OrderedDict([
                    ('get', OrderedDict([
                        ('produces', ['application/json'],),
                        ('parameters', [OrderedDict([
                            ('name', 'sample',),
                            ('in', 'query',),
                            ('required', False),
                            ('type', 'string',)])],),
                        ('responses', OrderedDict([
                            ('200', OrderedDict([
                                ('description', '200 response',),
                                ('schema', {'$ref': '#/definitions/Sample'},)])),
                        ]),),
                    ]),),
                ]),),
            ]),),
            ('definitions', OrderedDict([
                ('Sample', OrderedDict([
                    ('type', 'object',),
                ]),),
            ]),),
        ])

        return init_api

    def write(self, conf, path):
        txt = yaml.dump(
            conf,
            default_flow_style=False,
            allow_unicode=False)
        open(path, 'w').write(self.unescape(txt))

    def store_secret(self, key, value):
        conf = self.load_raw_secret()

        if 'cipher_texts' not in conf:
            conf['cipher_texts'] = {}

        conf['cipher_texts'][key] = value
        self.write(conf, self.get_secret_file())

    def store_secret_file(self, key, value):
        conf = self.load_raw_secret()

        if 'secret_files' not in conf:
            conf['secret_files'] = {}

        conf['secret_files'][key] = value
        self.write(conf, self.get_secret_file())

    def save_api_id(self, api_id):
        conf = self.load_raw_api()
        conf['api_id'] = str(api_id)
        self.write(conf, self.get_api_file())
