# -*- coding: utf-8 -*-

from lamvery.actions.base import BaseAction


class EncryptAction(BaseAction):

    def __init__(self, args):
        super(EncryptAction, self).__init__(args)
        self._text = args.text
        self._name = args.secret_name
        self._store = args.store

    def action(self):
        cipher_text = self.get_kms_client().encrypt(
            self._config.get_secret().get('key_id'), self._text)

        if self._store:
            self._config.store_secret(self._name, cipher_text)
        else:
            print(cipher_text)
