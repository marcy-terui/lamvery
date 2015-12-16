# -*- coding: utf-8 -*-

import yaml
import os
import logging
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from termcolor import colored
from lamvery.archive import Archive
from lamvery.client import Client
from lamvery.config import Config
from lamvery.log import get_logger

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

    _logger = None

    def __init__(self, args):
        self._config = Config(args.conf_file)

        if hasattr(args, 'dry_run') and args.dry_run:
            self._logger = get_logger('(Dry run) lamvery')
        else:
            self._logger = get_logger('lamvery')

    @abstractmethod
    def action(self):
        raise NotImplementedError

    def get_client(self):
        return Client(
            region=self._config.get_region(),
            profile=self._config.get_profile())

class InitAction(BaseAction):

    def __init__(self, args):
        super(InitAction, self).__init__(args)
        self._conf_file = args.conf_file

    def action(self):
        self._logger.info('Start initialization...')
        if self._needs_write_conf():
            self._config.write_default()
            self._logger.info(
                'Output initial configuration file to {}'.format(self._conf_file))

    def _needs_write_conf(self):
        ret = True
        if self._config.file_exists():
            y_n = raw_input(
                colored('Overwrite {}? [y/n]: '.format(self._conf_file), 'yellow'))
            if y_n != 'y':
                ret = False
        return ret

class ArchiveAction(BaseAction):

    def action(self):
        self._logger.info('Start archiving...')
        archive_name = self._config.get_archive_name()
        secret = self._config.generate_lambda_secret()
        archive = Archive(archive_name, secret)
        zipfile = archive.create_zipfile()
        with open(archive_name, 'w') as f:
            f.write(zipfile.read())
        zipfile.close()
        self._logger.info('Output package zip file to {}'.format(archive_name))

class DeployAction(BaseAction):

    def __init__(self, args):
        super(DeployAction, self).__init__(args)
        self._dry_run = args.dry_run
        self._publish = args.publish
        self._set_alias = SetAliasAction(args)

    def action(self):
        self._logger.info('Start deployment...')
        archive_name = self._config.get_archive_name()
        secret = self._config.generate_lambda_secret()
        archive = Archive(archive_name, secret)
        func_name   = self._config.get_function_name()
        local_conf  = self._config.get_configuration()
        zipfile     = archive.create_zipfile()
        client      = self.get_client()
        remote_conf = client.get_function_conf(func_name)

        self._print_conf_diff(remote=remote_conf, local=local_conf)

        if not self._dry_run:
            if len(remote_conf) > 0:
                client.update_function_code(zipfile, local_conf, self._publish)
                client.update_function_conf(local_conf)
            else:
                client.create_function(zipfile, local_conf, self._publish)
        zipfile.close()
        self._set_alias.action()
        self._logger.info('Deploy finished.')

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

    def _print_conf_diff(self, remote, local):
        diff = self._get_conf_diff(remote, local)
        for k,v in diff.items():
            if v is None:
                self._logger.warn(
                    '[Configuration] {k}: No change'.format(k=k))
            else:
                self._logger.warn(
                    '[Configuration] {k}: {r} > {l}'.format(k=k, r=v[0], l=v[1]))

class SetAliasAction(BaseAction):

    def __init__(self, args):
        super(SetAliasAction, self).__init__(args)
        self._dry_run = args.dry_run
        self._alias = args.alias
        if hasattr(args, 'alias_version'):
            self._alias_version = args.alias_version
        else:
            self._alias_version = None

    def action(self):
        self._logger.info('Start alias setting...')
        alias_name = self._get_alias_name()
        version    = self._get_alias_version()
        func_name  = self._config.get_function_name()
        client     = self.get_client()

        if alias_name is not None:
            current_alias = client.get_alias(func_name, alias_name)
            self._print_alias_diff(alias_name, current_alias, version)

            if not self._dry_run:
                if len(current_alias) > 0:
                    client.update_alias(func_name, alias_name, version)
                else:
                    client.create_alias(func_name, alias_name, version)
        self._logger.info('Finish alias setting.')

    def _print_alias_diff(self, name, current, version):
        self._logger.warn(
            '[Alias] {name}: {cur} > {new}'.format(
                name=name, cur=current.get('FunctionVersion'), new=version))

    def _get_alias_name(self):
        if self._alias is not None:
            return self._alias
        return self._config.get_configuration().get('alias')

    def _get_alias_version(self):
        if self._alias_version is None:
            return '$LATEST'
        return self._alias_version

class EncryptAction(BaseAction):

    def __init__(self, args):
        super(EncryptAction, self).__init__(args)
        self._text = args.text
        self._name = args.secret_name
        self._store = args.store

    def action(self):
        client = self.get_client()
        cipher_text = self.get_client().encrypt(
            self._config.get_secret().get('key_id'), self._text)

        if self._store:
            self._config.store_secret(self._name, cipher_text)
        else:
            print(cipher_text)

class DecryptAction(BaseAction):

    def __init__(self, args):
        super(DecryptAction, self).__init__(args)
        self._name = args.secret_name

    def action(self):
        client = self.get_client()
        text = self.get_client().decrypt(
            self._config.get_secret().get('cipher_texts').get(self._name))
        print(text)
