# -*- coding: utf-8 -*-

from lamvery.actions.base import BaseAction
from lamvery.archive import Archive


class ArchiveAction(BaseAction):

    def __init__(self, args):
        super(ArchiveAction, self).__init__(args)
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
        zipfile = archive.create_zipfile()
        with open(archive_name, 'w') as f:
            f.write(zipfile.read())
        zipfile.close()
        self._logger.info('Output archive(zip) to {}'.format(archive_name))
