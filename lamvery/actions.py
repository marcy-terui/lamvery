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

    def __init__(self, args):
        self._conf_file = args.conf_file
        self._dry_run = args.dry_run
        self._alias = args.alias
        self._alias_version = args.alias_version

    def get_conf_data(self):
        return yaml.load(
            open(self._conf_file, 'r').read()).get('configuration')

    def get_function_name(self):
        if os.path.exists(self._conf_file):
            return self.get_conf_data().get('name')
        else:
            return os.path.basename(os.getcwd())

    def get_archive_name(self):
        return '{}.zip'.format(self.get_function_name())

    def get_region(self):
        if os.path.exists(self._conf_file):
            return self.get_conf_data().get('region')
        else:
            return None

    def get_alias_name(self):
        if self._alias is not None:
            return self._alias
        return self.get_conf_data().get('alias')

    def get_alias_version(self):
        if self._alias_version is None:
            return '$LATEST'
        return self._alias_version

    def init(self):
        if self._needs_write_conf():
            yaml.dump(
                self._get_default_conf(),
                open(self._conf_file, 'w'),
                default_flow_style=False,
                allow_unicode=True)
            print('Output initial configuration file to {}.'.format(self._conf_file))

    def _get_default_conf(self):
        init_config = OrderedDict()
        init_config['region']      = 'us-east-1'
        init_config['name']        = self.get_function_name()
        init_config['runtime']     = 'python2.7'
        init_config['role']        = 'arn:aws:iam::<your-account-number>:role/<role>'
        init_config['handler']     = 'lambda_function.lambda_handler'
        init_config['description'] = 'This is sample lambda function.'
        init_config['timeout']     = 10
        init_config['memory_size'] = 128
        init_config['publish']     = True
        init_config['alias']       = None
        init_yaml = OrderedDict()
        init_yaml['configuration'] = init_config
        return init_yaml

    def _needs_write_conf(self):
        ret = True
        if os.path.exists(self._conf_file):
            y_n = raw_input(
                colored('Overwrite {}? [y/n]: '.format(self._conf_file), 'yellow'))
            if y_n != 'y':
                ret = False
        return ret

    def archive(self):
        archive = Archive(self.get_archive_name())
        zipfile = archive.create_zipfile()
        with open(self.get_archive_name(), 'w') as f:
            f.write(zipfile.read())
        zipfile.close()
        print('Output package zip file to {}'.format(self.get_archive_name()))

    def deploy(self):
        archive     = Archive(self.get_archive_name())
        client      = Client(region=self.get_region())
        func_name   = self.get_function_name()
        remote_conf = client.get_function_conf(func_name)
        local_conf  = self.get_conf_data()
        zipfile     = archive.create_zipfile()

        self.print_conf_diff(remote=remote_conf, local=local_conf)

        if not self._dry_run:
            if len(remote_conf) > 0:
                client.update_function_code(zipfile, local_conf)
                client.update_function_conf(local_conf)
            else:
                client.create_function(zipfile, local_conf)
        zipfile.close()
        self.set_alias()

    def set_alias(self):
        alias_name = self.get_alias_name()
        version    = self.get_alias_version()
        func_name  = self.get_function_name()
        client     = Client(region=self.get_region())

        if alias_name is not None:
            current_alias = client.get_alias(func_name, alias_name)
            self.print_alias_diff(alias_name, current_alias, version)

            if not self._dry_run:
                if len(current_alias) > 0:
                    client.update_alias(func_name, alias_name, version)
                else:
                    client.create_alias(func_name, alias_name, version)

    def print_alias_diff(self, name, current, version):
        print('Alias update...')
        cprint(
            '[Alias] {name}: {cur} > {new}'.format(
                name=name,
                cur=current.get('FunctionVersion'),
                new=version),
            'yellow', attrs=['bold'])

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
        print('Configuration update...')
        diff = self._get_conf_diff(remote, local)
        for k,v in diff.items():
            if v is None:
                cprint('[Configuration] {k}: No change'.format(k=k), 'green')
            else:
                cprint('[Configuration] {k}: {r} > {l}'.format(k=k, r=v[0], l=v[1]), 'yellow', attrs=['bold'])
