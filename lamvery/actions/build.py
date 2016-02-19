# -*- coding: utf-8 -*-

from lamvery.actions.base import BaseAction
from lamvery.build import Builder
from lamvery.utils import parse_env_args


class BuildAction(BaseAction):

    def __init__(self, args):
        super(BuildAction, self).__init__(args)
        self._single_file = args.single_file
        self._no_libs = args.no_libs
        self._env = parse_env_args(args.env)

    def action(self):
        archive_name = self._config.get_archive_name()
        function_filename = self._config.get_function_filename()
        secret = self._config.generate_lambda_secret()
        exclude = self._config.get_exclude()

        builder = Builder(
            filename=archive_name,
            function_filename=function_filename,
            secret=secret,
            single_file=self._single_file,
            no_libs=self._no_libs,
            exclude=exclude,
            runtime=self._config.get_runtime(),
            env=self._env,
            clean_build=self._config.is_clean_build(),
            hooks=self._config.get_build_hooks())

        zipfile = builder.build()
        with open(archive_name, 'w') as f:
            f.write(zipfile.read())
        zipfile.close()

        self._logger.info('Output archive(zip) to {}'.format(archive_name))
