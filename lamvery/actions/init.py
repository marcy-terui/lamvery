# -*- coding: utf-8 -*-

from lamvery.actions.base import BaseAction
from lamvery.utils import confirm_overwrite


class InitAction(BaseAction):

    def __init__(self, args):
        super(InitAction, self).__init__(args)
        self._conf_file = args.conf_file

    def action(self):
        if confirm_overwrite(self._conf_file):
            self._config.write(self._config.get_default(), self._conf_file)
            self._logger.info(
                'Output initial file: {}'.format(self._conf_file))

        files = {
            self._config.get_event_file(): self._config.get_default_events(),
            self._config.get_secret_file(): self._config.get_default_secret(),
            self._config.get_exclude_file(): self._config.get_default_exclude(),
            self._config.get_hook_file(): self._config.get_default_hook(),
            self._config.get_api_file(): self._config.get_default_api(),
        }

        for f, c in files.items():
            if confirm_overwrite(f):
                self._config.write(c, f)
                self._logger.info(
                    'Output initial file: {}'.format(f))
