# -*- coding: utf-8 -*-

from lamvery.actions.base import BaseAction


class EncryptFileAction(BaseAction):

    def __init__(self, args):
        super(EncryptFileAction, self).__init__(args)
        self._file = args.file
        self._path = args.path
        self._store = args.store

    def action(self):
        cipher_text = self.get_kms_client().encrypt(
            self._config.get_secret().get('key_id'), open(self._path, 'r').read())

        if self._store:
            self._config.store_secret_file(self._file, cipher_text)
        else:
            print(cipher_text)
