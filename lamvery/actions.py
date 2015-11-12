# -*- coding: utf-8 -*-

import yaml
import os
from termcolor import cprint, colored
from collections import OrderedDict
from lamvery.archive import Archive
from lamvery.client import Client

CONF_DIFF_KEYS = [
    ('Runtime', 'runtime',),
    ('Role', 'role',),
    ('Handler', 'handler',),
    ('Description', 'description',),
    ('Timeout', 'timeout',),
    ('MemorySize', 'memory_size',),
]


def represent_odict(dumper, instance):
     return dumper.represent_mapping(u'tag:yaml.org,2002:map', instance.items())

yaml.add_representer(OrderedDict, represent_odict)

class Actions(object):

    def __init__(self, conf, dry_run):
        self._conf = conf
        self._dry_run = dry_run
        self._archive = Archive(self.get)
        self._client = Client()

    def get_conf_data(self):
        return yaml.load(
            open(self._conf, 'r').read()).get('configuration')

    def get_function_name(self):
        if os.path.exists(self._conf):
            return self.get_conf_data().get('name')
        else:
            return os.path.basename(os.getcwd())

    def get_archive_name(self):
        return '{}.zip'.format(self.get_function_name())

    def init(self):
        init_config = OrderedDict()
        init_config['name']        = 'sample_lambda_function'
        init_config['runtime']     = 'python2.7'
        init_config['role']        = 'arn:aws:iam::<your-account-number>:role/<role>'
        init_config['handler']     = 'lambda_function.lambda_handler'
        init_config['description'] = 'This is sample lambda function.'
        init_config['timeout']     = 10
        init_config['memory_size'] = 128
        init_config['publish']     = True
        init_yaml = OrderedDict()
        init_yaml['configuration'] = init_config

        write = True
        if os.path.exists(self._conf):
            y_n = raw_input(
                colored('Overwrite {}? [y/n]: '.format(self._conf), 'yellow'))
            if y_n != 'y':
                write = False
        if write:
            yaml.dump(
                init_yaml,
                open(self._conf, 'w'),
                default_flow_style=False,
                allow_unicode=True)
            print('Output initial configuration file to {}.'.format(self._conf))

    def archive(self):
        zipfile = self._archive.create_zipfile()
        with open(self.get_archive_name(), 'w') as f:
            f.write(zipfile.read())
        zipfile.close()
        print('Output package zip file to {}'.format(self.get_archive_name()))

    def deploy(self):
        func_name = self.get_function_name()
        remote_conf = self._client.get_function_conf(func_name)
        local_conf = self.get_conf_data()
        zipfile = self._archive.create_zipfile()
        self.print_conf_diff(remote=remote_conf, local=local_conf)
        if self._dry_run:
            return
        if len(remote_conf) > 0:
            self._client.update_function_code(zipfile, local_conf)
            self._client.update_function_conf(local_conf)
        else:
            self._client.create_function(zipfile, local_conf)
        zipfile.close()
        print('Deploy finished!')

    def _get_conf_diff(self, remote, local):
        diff = {}
        for k in CONF_DIFF_KEYS:
            r = remote.get(k[0])
            l = local.get(k[1])
            if r == l:
                diff[k[1]] = None
            else:
                diff[k[1]] = (r, l,)
        return diff

    def print_conf_diff(self, remote, local):
        diff = self._get_conf_diff(remote, local)
        for k,v in diff.iteritems():
            if v is None:
                cprint('{k}: No change'.format(k=k), 'green')
            else:
                cprint('{k}: {r} > {l}'.format(k=k, r=v[0], l=v[1]), 'yellow', attrs=['bold'])
