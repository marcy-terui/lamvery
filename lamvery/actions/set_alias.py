# -*- coding: utf-8 -*-

from lamvery.actions.base import BaseAction


class SetAliasAction(BaseAction):

    def __init__(self, args):
        super(SetAliasAction, self).__init__(args)

        if hasattr(args, 'target'):
            self._target = args.target
        else:
            self._target = None

        if hasattr(args, 'version'):
            self._version = args.version
        else:
            self._version = None

    def action(self):
        alias_name = self.get_alias_name()
        func_name = self._config.get_function_name()
        version = self.get_version(func_name)
        client = self.get_lambda_client()

        if alias_name is None:
            raise Exception(
                'Please specify an alias by `-a` option or `default_alias` configuration.')

        current_alias = client.get_alias(func_name, alias_name)
        self._print_alias_diff(alias_name, current_alias, version)

        if len(current_alias) > 0:
            client.update_alias(func_name, alias_name, version)
        else:
            client.create_alias(func_name, alias_name, version)

    def _print_alias_diff(self, name, current, version):
        self._logger.warn(
            '[Alias] {name}: {cur} -> {new}'.format(
                name=name, cur=current.get('FunctionVersion'), new=version))

    def get_version(self, function):
        version = '$LATEST'

        if self._version is not None:
            version = self._version

        elif self._target is not None:
            target_alias = self.get_lambda_client().get_alias(function, self._target)
            version = target_alias.get('FunctionVersion')

            if version is None:
                raise Exception(
                    'Target alias "{}" does not exist in "{}" function.'.format(
                        self._target, function))

        return version
