# -*- coding: utf-8 -*-

from termcolor import colored
from lamvery.actions.base import BaseAction

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
