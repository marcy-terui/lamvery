# -*- coding: utf-8 -*-

import base64
import os
from lamvery.actions.base import BaseAction
from termcolor import cprint


class InvokeAction(BaseAction):

    def __init__(self, args):
        super(InvokeAction, self).__init__(args)

        if os.path.exists(args.json):
            self._json = open(args.json, 'r').read()
        else:
            self._json = args.json

        if args.alias is None:
            self._alias = self._config.get_default_alias()
        else:
            self._alias = args.alias

        self._version = args.version

    def action(self):
        qualifier = self._alias
        client = self.get_lambda_client()

        if self._version is not None:
            qualifier = self._version

        ret = client.invoke(
            name=self._config.get_function_name(),
            qualifier=qualifier,
            payload=self._json)

        if ret.get('FunctionError') is None:
            cprint(base64.b64decode(ret.get('LogResult')), 'green')
        else:
            self._logger.error('{} error occurred'.format(ret.get('FunctionError')))
            cprint(base64.b64decode(ret.get('LogResult')), 'red')
