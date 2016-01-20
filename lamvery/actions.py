# -*- coding: utf-8 -*-

import yaml
import os
import logging
import datetime
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

EVENT_RULE_DIFF_KEYS = [
    ('Description', 'description',),
    ('EventPattern', 'pattern',),
    ('RoleArn', 'role',),
    ('ScheduleExpression', 'schedule',),
    ('State', 'state',),
]

class BaseAction:

    __metaclass__ = ABCMeta

    _logger = None

    def __init__(self, args):
        self._config = Config(args.conf_file)

        if hasattr(args, 'dry_run'):
            self._dry_run = args.dry_run

            if self._dry_run:
                self._logger = get_logger('(Dry run) lamvery')
                self._dry_run = args.dry_run
            else:
                self._logger = get_logger('lamvery')

    @abstractmethod
    def action(self):
        raise NotImplementedError

    def get_client(self):
        return Client(
            region=self._config.get_region(),
            profile=self._config.get_profile(),
            dry_run=self._dry_run)

    def _get_diff(self, remote, local, keys):
        diff = {}
        for k in keys:
            r = remote.get(k[0])
            l = local.get(k[1])
            if r == l:
                diff[k[1]] = None
            else:
                diff[k[1]] = (r, l,)
        return diff

    def _print_diff(self, name, remote, local, keys):
        diff = self._get_diff(remote, local, keys)
        for k,v in diff.items():
            if v is not None:
                self._logger.warn(
                    '[{n}] {k}: {r} -> {l}'.format(n=name, k=k, r=v[0], l=v[1]))

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

    def __init__(self, args):
        super(ArchiveAction, self).__init__(args)
        self._no_libs = args.no_libs

    def action(self):
        self._logger.info('Start archiving...')
        archive_name = self._config.get_archive_name()
        secret = self._config.generate_lambda_secret()
        archive = Archive(filename=archive_name,
                          secret=secret,
                          no_libs=self._no_libs)
        zipfile = archive.create_zipfile()
        with open(archive_name, 'w') as f:
            f.write(zipfile.read())
        zipfile.close()
        self._logger.info('Output archive(zip) to {}'.format(archive_name))

class ConfigureAction(BaseAction):

    def __init__(self, args):
        super(ConfigureAction, self).__init__(args)

    def action(self):
        self._logger.info('Start configuring...')
        func_name   = self._config.get_function_name()
        local_conf  = self._config.get_configuration()
        client      = self.get_client()
        remote_conf = client.get_function_conf(func_name)

        if len(remote_conf) > 0:
            self._print_diff(
                name='Function - Configuration',
                remote=remote_conf, local=local_conf, keys=CONF_DIFF_KEYS)
            client.update_function_conf(local_conf)
        else:
            msg = '"{}" function is not exists. Please `deploy` at first.'.format(func_name)
            raise Exception(msg)

        self._logger.info('Finish configuring.')

class DeployAction(ConfigureAction):

    def __init__(self, args):
        super(DeployAction, self).__init__(args)
        self._publish = args.publish
        self._set_alias = SetAliasAction(args)
        self._no_libs = args.no_libs

    def action(self):
        self._logger.info('Start deployment...')
        archive_name = self._config.get_archive_name()
        secret = self._config.generate_lambda_secret()
        archive = Archive(filename=archive_name,
                          secret=secret,
                          no_libs=self._no_libs)
        func_name   = self._config.get_function_name()
        local_conf  = self._config.get_configuration()
        zipfile     = archive.create_zipfile()
        client      = self.get_client()
        remote_conf = client.get_function_conf(func_name)

        if len(remote_conf) == 0:
            self._logger.warn(
                '[Function] Create new function "{}"'.format(func_name))

        self._print_diff(
            name='Function - Configuration',
            remote=remote_conf, local=local_conf, keys=CONF_DIFF_KEYS)

        self._print_capacity(
            remote=client.calculate_capacity(),
            local=archive.get_size())

        if len(remote_conf) > 0:
            client.update_function_code(zipfile, local_conf, self._publish)
            client.update_function_conf(local_conf)
        else:
            client.create_function(zipfile, local_conf, self._publish)
        zipfile.close()
        self._set_alias.action()
        self._logger.info('Finish deployment.')

    def _print_capacity(self, remote, local):
        self._logger.warn(
            '[Function - Capacity] {r} Bytes -> {t} Bytes'.format(
                r='{:,d}'.format(remote), t='{:,d}'.format(remote + local)))

class SetAliasAction(BaseAction):

    def __init__(self, args):
        super(SetAliasAction, self).__init__(args)
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

            if len(current_alias) > 0:
                client.update_alias(func_name, alias_name, version)
            else:
                client.create_alias(func_name, alias_name, version)
        self._logger.info('Finish alias setting.')

    def _print_alias_diff(self, name, current, version):
        self._logger.warn(
            '[Function - Alias] {name}: {cur} -> {new}'.format(
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

class EventsAction(BaseAction):

    def __init__(self, args):
        super(EventsAction, self).__init__(args)
        self._keep_empty = args.keep_empty_events

    def action(self):
        self._logger.info('Start events setting...')
        client = self.get_client()
        func_name  = self._config.get_function_name()
        conf = client.get_function_conf(func_name)

        if len(conf) < 0:
            msg = '"{}" function is not exists. Please `deploy` at first.'.format(func_name)
            raise Exception(msg)

        arn = conf['FunctionArn']
        local_rules = self._config.get_events()
        remote_rules = client.get_rules_by_target(arn)

        self._put_rules(remote_rules, local_rules)
        self._put_target(local_rules, arn)
        self._clean(remote_rules, local_rules, arn)
        self._logger.info('Finish events setting.')

    def _put_rules(self, remote, local):
        client = self.get_client()

        for l in local:
            l['state'] = self._convert_state(l.get('disabled'))

            r = self._search_rule(remote, l['rule'])
            if len(r) == 0:
                self._logger.warn(
                    '[EventRule] Create new event rule "{}"'.format(l['rule']))

            self._print_diff(
                name='EventRule - {}'.format(l['rule']),
                keys=EVENT_RULE_DIFF_KEYS,
                remote=r, local=l)

            client.put_rule(l)

    def _convert_state(self, disabled):
        if disabled:
            return 'DISABLED'
        else:
            return 'ENABLED'

    def _search_rule(self, rules, name):
        for r in rules:
            if name in [r.get('Name'), r.get('rule')]:
                return r
        return {}

    def _exist_rule(self, rules, name):
        return len(self._search_rule(rules, name)) > 0

    def _exist_target(self, targets, arn):
        for t in targets:
            if t['Arn'] == arn:
                return True
        return False

    def _put_target(self, local, arn):
        client = self.get_client()

        for l in local:
            targets = client.get_targets_by_rule(l['rule'])

            if self._exist_target(targets, arn):
                break

            self._logger.warn(
                '[EventRule - {name}] Add "{arn}" to targets'.format(name=l['rule'], arn=arn))
            client.put_target(
                rule=l['rule'], target=self._generate_target_id(l['rule'], arn), arn=arn)

    def _generate_target_id(self, rule, arn):
        ret = '{}-{}_{}'.format(
            rule,
            arn[arn.rfind(':')+1:],
            datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        )
        return ret[0:64]

    def _clean(self, remote, local, arn):
        client = self.get_client()

        for r in remote:
            if not self._exist_rule(local, r['Name']):
                targets = client.get_targets_by_rule(r['Name'])

                target_ids = []
                for t in targets:
                    if arn == t['Arn']:
                        self._logger.warn(
                            '[EventRule {}] Remove event target "{}"'.format(r['Name'], t['Id']))
                        target_ids.append(t['Id'])
                client.remove_targets(r['Name'], target_ids)

                if len(targets) == 1 and not self._keep_empty:
                    self._logger.warn('[EventRule] Delete the event rule "{}" that does not have any targets'.format(r['Name']))
                    client.delete_rule(r['Name'])
