# -*- coding: utf-8 -*-

from lamvery.actions.configure import (
    ConfigureAction, CONF_DIFF_KEYS)
from lamvery.actions.set_alias import SetAliasAction
from lamvery.archive import Archive

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
        exclude = self._config.get_exclude()
        archive = Archive(filename=archive_name,
                          secret=secret,
                          no_libs=self._no_libs,
                          exclude=exclude)
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


        remote_size=client.calculate_capacity()
        local_size=archive.get_size()

        if len(remote_conf) > 0:
            if not self._publish:
                local_size -= remote_conf['CodeSize']
            self._print_capacity(remote=remote_size, local=local_size)
            client.update_function_code(zipfile, local_conf, self._publish)
            client.update_function_conf(local_conf)
        else:
            if self._publish:
                local_size *= 2
            self._print_capacity(remote=remote_size, local=local_size)
            client.create_function(zipfile, local_conf, self._publish)
        zipfile.close()
        self._set_alias.action()
        self._logger.info('Finish deployment.')

    def _print_capacity(self, remote, local):
        self._logger.warn(
            '[Function - Capacity] {r} Bytes -> {t} Bytes'.format(
                r='{:,d}'.format(remote), t='{:,d}'.format(remote + local)))
