# -*- coding: utf-8 -*-

import os
import sys
from termcolor import cprint
from lamvery.actions.base import BaseAction


class InitAction(BaseAction):

    def __init__(self, args):
        super(InitAction, self).__init__(args)
        self._conf_file = args.conf_file

    def action(self):
        if self._needs_write(self._conf_file):
            self._config.write(self._config.get_default(), self._conf_file)
            self._logger.info(
                'Output initial file: {}'.format(self._conf_file))

        files = {
            self._config.get_event_file(): self._config.get_default_events(),
            self._config.get_secret_file(): self._config.get_default_secret(),
            self._config.get_exclude_file(): self._config.get_default_exclude(),
        }
        
        for f, c in files.items():
            if self._needs_write(f):
                self._config.write(c, f)
                self._logger.info(
                    'Output initial file: {}'.format(f))

    def _needs_write(self, path):
        ret = True
        if os.path.exists(path):
            cprint('Overwrite {}? [y/n]: '.format(path), 'yellow', file=sys.stderr, end="")
            y_n = sys.stdin.readline()
            if not y_n.startswith('y'):
                ret = False
        return ret
