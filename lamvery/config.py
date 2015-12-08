# -*- coding: utf-8 -*-

import yaml
import os
from termcolor import cprint, colored
from collections import OrderedDict
from lamvery.archive import Archive
from lamvery.client import Client

def represent_odict(dumper, instance):
     return dumper.represent_mapping(u'tag:yaml.org,2002:map', instance.items())

yaml.add_representer(OrderedDict, represent_odict)

class Config:

    def __init__(self, conf_file):
        self._file = conf_file

    def load_conf(self):
        return yaml.load(open(self._file, 'r').read())

    def get_configuration(self):
        return self.load_conf().get('configuration')

    def get_secret(self):
        return self.load_conf().get('secret')

    def get_function_name(self):
        if os.path.exists(self._file):
            return self.get_configuration().get('name')
        else:
            return os.path.basename(os.getcwd())

    def get_archive_name(self):
        return '{}.zip'.format(self.get_function_name())

    def get_region(self):
        if os.path.exists(self._file):
            return self.get_configuration().get('region')
        else:
            return None

    def get_alias_name(self):
        if self._alias is not None:
            return self._alias
        return self.get_configuration().get('alias')

    def get_alias_version(self):
        if self._alias_version is None:
            return '$LATEST'
        return self._alias_version

    def get_profile(self):
        return self.load_conf().get('profile')

    def get_default(self):
        init_config = OrderedDict()
        init_config['region']      = 'us-east-1'
        init_config['name']        = self.get_function_name()
        init_config['runtime']     = 'python2.7'
        init_config['role']        = 'arn:aws:iam::<account-number>:role/<role>'
        init_config['handler']     = 'lambda_function.lambda_handler'
        init_config['description'] = 'This is sample lambda function.'
        init_config['timeout']     = 10
        init_config['memory_size'] = 128

        init_secret = OrderedDict()
        init_secret['key'] = 'arn:aws:kms:<region>:<account-number>:key/<key-id>'
        init_secret['cipher_texts'] = OrderedDict()

        init_yaml = OrderedDict()
        init_yaml['profile'] = None
        init_yaml['configuration'] = init_config
        init_yaml['secret'] = init_secret

        return init_yaml

    def write_default(self):
        yaml.dump(
            self.get_default(),
            open(self._file, 'w'),
            default_flow_style=False,
            allow_unicode=True)

    def file_exists(self):
        return os.path.exists(self._file)
