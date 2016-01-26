# -*- coding: utf-8 -*-

from lamvery.actions.base import BaseAction
from lamvery.archive import Archive

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
