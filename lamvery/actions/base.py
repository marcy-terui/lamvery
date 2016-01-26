# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from lamvery.client import Client
from lamvery.config import Config
from lamvery.log import get_logger

class BaseAction:

    __metaclass__ = ABCMeta

    _logger = None

    def __init__(self, args):
        self._config = Config(args.conf_file)
        self._dry_run = False

        logger_name = 'lamvery'
        if hasattr(args, 'dry_run'):
            self._dry_run = args.dry_run
            if self._dry_run:
                logger_name = '(Dry run) lamvery'

        self._logger = get_logger(logger_name)

    @abstractmethod
    def action(self):
        raise NotImplementedError

    def get_client(self):
        return Client(
            region=self._config.get_region(),
            profile=self._config.get_profile(),
            dry_run=self._dry_run)

    def _get_diff(self, remote, local, keys):
        diff = {}
        for k in keys:
            r = remote.get(k[0])
            l = local.get(k[1])
            if r == l:
                diff[k[1]] = None
            else:
                diff[k[1]] = (r, l,)
        return diff

    def _print_diff(self, prefix, remote, local, keys):
        diff = self._get_diff(remote, local, keys)
        for k,v in diff.items():
            if v is not None:
                self._logger.warn(
                    '{p} {k}: {r} -> {l}'.format(p=prefix, k=k, r=v[0], l=v[1]))
