# -*- coding: utf-8 -*-

import base64
import os
from lamvery.actions.base import BaseAction

class InvokeAction(BaseAction):

    def __init__(self, args):
        super(InvokeAction, self).__init__(args)

        if os.path.exists(args.json):
            self._json = open(args.json, 'r').read()
        else:
            self._json = args.json
        self._version = args.version
        self._alias = args.alias

    def action(self):
        qualifier = self._alias
        client = self.get_client()
        
        if self._version is not None:
            qualifier = self._version

        ret = client.invoke(
            name=self._config.get_function_name(),
            qualifier=qualifier,
            payload=self._json)

        log = """
========== LOG START ==========

{}
========== LOG END ==========""".format(base64.b64decode(ret.get('LogResult')))

        if ret.get('FunctionError') is None:
            self._logger.info(log)
        else:
            self._logger.error('{} error occurred'.format(ret.get('FunctionError')))
            self._logger.error(log)
