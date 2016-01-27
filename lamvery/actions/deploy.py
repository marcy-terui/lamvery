# -*- coding: utf-8 -*-

from lamvery.actions.base import BaseAction
from lamvery.actions.configure import CONF_DIFF_KEYS
from lamvery.actions.set_alias import SetAliasAction
from lamvery.archive import Archive
from lamvery.utils import previous_alias

class DeployAction(BaseAction):

    def __init__(self, args):
        super(DeployAction, self).__init__(args)
        self._publish = args.publish
        self._set_alias = SetAliasAction(args)
        self._single_file = args.single_file
        self._no_libs = args.no_libs

    def action(self):
        archive_name = self._config.get_archive_name()
        function_filename = self._config.get_function_filename()
        secret = self._config.generate_lambda_secret()
        exclude = self._config.get_exclude()
        archive = Archive(filename=archive_name,
                          function_filename=function_filename,
                          secret=secret,
                          single_file=self._single_file,
                          no_libs=self._no_libs,
                          exclude=exclude)
        func_name   = self._config.get_function_name()
        local_conf  = self._config.get_configuration()
        zipfile     = archive.create_zipfile()
        client      = self.get_client()
        remote_conf = client.get_function_conf(func_name)
        alias_name  = self._set_alias.get_alias_name()
        remote_size = client.calculate_capacity()
        local_size  = archive.get_size()
        new_version = None
        cur_version = None

        if len(remote_conf) == 0:
            self._logger.warn(
                '[Function] Create new function "{}"'.format(func_name))

        self._print_diff(
            prefix='[Function]',
            remote=remote_conf, local=local_conf, keys=CONF_DIFF_KEYS)

        if len(remote_conf) > 0:

            if self._enable_versioning():
                cur_version = client.get_alias(
                    func_name, alias_name).get('FunctionVersion')
            else:
                local_size -= remote_conf['CodeSize']

            client.update_function_conf(local_conf)
            self._print_capacity(remote=remote_size, local=local_size)
            new_version = client.update_function_code(
                zipfile, local_conf, self._enable_versioning())

        else:
            if self._enable_versioning():
                local_size *= 2

            self._print_capacity(
                remote=remote_size, local=local_size)
            new_version = client.create_function(
                zipfile, local_conf, self._enable_versioning())

        zipfile.close()

        if new_version is not None:
            self._logger.info(
                '[Function] Deployed version: {}'.format(new_version))

        if cur_version is not None:
            self._logger.info(
                '[Function] Previous version: {}'.format(cur_version))
            self._set_alias._alias = previous_alias(alias_name)
            self._set_alias._version = cur_version
            self._set_alias.action()

        self._set_alias._alias = alias_name
        self._set_alias._version = new_version
        self._set_alias.action()

    def _enable_versioning(self):
        if self._publish:
            return True
        return self._config.enable_versioning()

    def _print_capacity(self, remote, local):
        self._logger.warn(
            '[Function] Capacity: {r} Bytes -> {t} Bytes'.format(
                r='{:,d}'.format(remote), t='{:,d}'.format(remote + local)))
