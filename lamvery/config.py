# -*- coding: utf-8 -*-

import yaml
import os
import uuid
from termcolor import cprint, colored
from collections import OrderedDict
from lamvery.archive import Archive
from lamvery.client import Client
from jinja2 import Environment, FileSystemLoader

def represent_odict(dumper, instance):
     return dumper.represent_mapping(u'tag:yaml.org,2002:map', instance.items())

yaml.add_representer(OrderedDict, represent_odict)
yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    lambda loader, node: OrderedDict(loader.construct_pairs(node)))

class Config:

    def __init__(self, conf_file):
        self._file = conf_file
        self._template_env = Environment(loader=FileSystemLoader('./', encoding='utf8'))

    def load_conf(self):
        tmpl = self._template_env.get_template(self._file)
        return yaml.load(tmpl.render({'env': os.environ}))

    def load_raw_conf(self):
        txt = open(self._file, 'r').read()
        return yaml.load(self.escape(txt))

    def escape(self, txt):
        txt = txt.replace("'", "''")
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
        txt = txt.replace("''", "'")
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

    def get_secret(self):
        return self.load_conf().get('secret')

    def generate_lambda_secret(self):
        return {
            'region': self.get_region(),
            'cipher_texts': self.get_secret().get('cipher_texts')
        }

    def get_function_name(self):
        if os.path.exists(self._file):
            return self.get_configuration().get('name')
        else:
            return os.path.basename(os.getcwd())

    def get_archive_name(self):
        return '{}.zip'.format(self.get_function_name())

    def get_region(self):
        if os.path.exists(self._file):
            return self.load_conf().get('region')
        else:
            return None

    def get_profile(self):
        return self.load_conf().get('profile')

    def get_default(self):
        init_config = OrderedDict()
        init_config['name']        = self.get_function_name()
        init_config['runtime']     = 'python2.7'
        init_config['role']        = 'arn:aws:iam::<account-number>:role/<role>'
        init_config['handler']     = 'lambda_function.lambda_handler'
        init_config['description'] = 'This is sample lambda function.'
        init_config['timeout']     = 10
        init_config['memory_size'] = 128

        init_secret = OrderedDict()
        init_secret['key_id'] = '<key-id>'
        init_secret['cipher_texts'] = OrderedDict()

        init_yaml = OrderedDict()
        init_yaml['profile'] = None
        init_yaml['region']  = 'us-east-1'
        init_yaml['configuration'] = init_config
        init_yaml['secret'] = init_secret

        return init_yaml

    def write_default(self):
        self.write(self.get_default())

    def write(self, conf):
        txt = yaml.dump(
            conf,
            default_flow_style=False,
            allow_unicode=True)
        open(self._file, 'w').write(self.unescape(txt))

    def file_exists(self):
        return os.path.exists(self._file)

    def store_secret(self, key, value):
        conf = self.load_raw_conf()
        default = self.get_default()

        if 'secret' not in conf:
            conf['secret'] = default['secret']
        elif 'cipher_texts' not in conf['secret']:
            conf['secret']['cipher_texts'] = {}

        conf['secret']['cipher_texts'][key] = value
        self.write(conf)
