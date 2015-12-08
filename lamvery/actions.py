# -*- coding: utf-8 -*-

import yaml
import os
import logging
from abc import ABCMeta, abstractmethod
from termcolor import cprint, colored
from collections import OrderedDict
from lamvery.archive import Archive
from lamvery.client import Client
from lamvery.config import Config

CONF_DIFF_KEYS = [
    ('Runtime', 'runtime',),
    ('Role', 'role',),
    ('Handler', 'handler',),
    ('Description', 'description',),
    ('Timeout', 'timeout',),
    ('MemorySize', 'memory_size',),
]

class BaseAction:

    __metaclass__ = ABCMeta

    def __init__(self, args):
        self._args = args
        self._config = Config(args.conf_file)

        logging.basicConfig(format='%(name)s: %(message)s', level=logging.INFO)
        if hasattr(args, 'dry_run') and args.dry_run:
            self._logger = logging.getLogger('(Dry run) lamvery')
        else:
            self._logger = logging.getLogger('lamvery')

    @abstractmethod
    def action(self):
        raise NotImplementedError

class InitAction(BaseAction):

    def action(self):
        self._logger.info(
            colored('Start initialization...', 'green'))
        if self._needs_write_conf():
            self._config.write_default()
            self._logger.info(
                colored('Output initial configuration file to {}.'.format(self._config._file), 'green'))

    def _needs_write_conf(self):
        ret = True
        if self._config.file_exists():
            y_n = raw_input(
                colored('Overwrite {}? [y/n]: '.format(self._config._file), 'yellow'))
            if y_n != 'y':
                ret = False
        return ret

class ArchiveAction(BaseAction):

    def action(self):
        self._logger.info(
            colored('Start archiving...', 'green'))
        archive_name = self._config.get_archive_name()
        archive = Archive(archive_name)
        zipfile = archive.create_zipfile()
        with open(archive_name, 'w') as f:
            f.write(zipfile.read())
        zipfile.close()
        self._logger.info(
            colored('Output package zip file to {}'.format(archive_name), 'green'))

class DeployAction(BaseAction):

    def __init__(self, args):
        super(DeployAction, self).__init__(args)
        self._dry_run = args.dry_run
        self._publish = args.publish

    def action(self):
        self._logger.info(
            colored('Start deployment...', 'green'))
        archive     = Archive(self._config.get_archive_name())
        func_name   = self._config.get_function_name()
        local_conf  = self._config.get_configuration()
        zipfile     = archive.create_zipfile()
        client = Client(
            region=self._config.get_region(),
            profile=self._config.get_profile())
        remote_conf = client.get_function_conf(func_name)

        self.print_conf_diff(remote=remote_conf, local=local_conf)

        if not self._dry_run:
            if len(remote_conf) > 0:
                client.update_function_code(zipfile, local_conf, self._publish)
                client.update_function_conf(local_conf)
            else:
                client.create_function(zipfile, local_conf, self._publish)
        zipfile.close()
        SetAliasAction(self.args).action()
        self._logger.info(
            colored('Deploy finished.', 'green'))

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
        for k,v in diff.items():
            if v is None:
                self._logger.info(
                    colored('[Configuration] {k}: No change'.format(k=k), 'green'))
            else:
                self._logger.info(
                    colored('[Configuration] {k}: {r} > {l}'.format(k=k, r=v[0], l=v[1]), 'yellow'))

class SetAliasAction(BaseAction):

    def __init__(self, args):
        super(SetAliasAction, self).__init__(args)
        self._dry_run = args.dry_run

    def action(self):
        self._logger.info(
            colored('Start alias setting...', 'green'))
        alias_name = self._config.get_alias_name()
        version    = self._config.get_alias_version()
        func_name  = self._config.get_function_name()
        client = Client(
            region=self._config.get_region(),
            profile=self._config.get_profile())

        if alias_name is not None:
            current_alias = client.get_alias(func_name, alias_name)
            self.print_alias_diff(alias_name, current_alias, version)

            if not self._dry_run:
                if len(current_alias) > 0:
                    client.update_alias(func_name, alias_name, version)
                else:
                    client.create_alias(func_name, alias_name, version)
        self._logger.info(
            colored('Finish alias setting.', 'green'))

    def print_alias_diff(self, name, current, version):
        self._logger.info(colored(
            '[Alias] {name}: {cur} > {new}'.format(
                name=name, cur=current.get('FunctionVersion'), new=version), 'yellow'))
