# -*- coding: utf-8 -*-

from lamvery.actions.base import BaseAction


class DecryptAction(BaseAction):

    def __init__(self, args):
        super(DecryptAction, self).__init__(args)
        self._name = args.secret_name

    def action(self):
        text = self.get_kms_client().decrypt(
            self._config.get_secret().get('cipher_texts').get(self._name))
        print(text)
