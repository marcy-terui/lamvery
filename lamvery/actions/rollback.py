# -*- coding: utf-8 -*-

from lamvery.actions.base import BaseAction
from lamvery.actions.set_alias import SetAliasAction


class RollbackAction(BaseAction):

    def __init__(self, args):
        super(RollbackAction, self).__init__(args)
        self._set_alias = SetAliasAction(args)

    def action(self):
        func_name = self._config.get_function_name()
        client = self.get_lambda_client()
        remote_conf = client.get_function_conf(func_name)
        alias_name = self._set_alias.get_alias_name()

        if len(remote_conf) == 0:
            raise Exception(
                '"{}" function is not exists. Please `deploy` at first.'.format(func_name))

        pre_version = client.get_previous_version(func_name, alias_name)
        if pre_version is None:
            raise Exception(
                'There is no previous version. ' +
                'Please `deploy` with `publish` option or `versioning` configuration.')

        self._logger.info(
            '[Function] Previous version: {}'.format(pre_version))

        self._set_alias._version = pre_version
        self._set_alias.action()
