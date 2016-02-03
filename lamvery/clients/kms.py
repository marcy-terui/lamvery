# -*- coding: utf-8 -*-

import base64

from lamvery.clients.base import BaseClient


class KmsClient(BaseClient):

    def __init__(self, *args, **kwargs):
        super(KmsClient, self).__init__(*args, **kwargs)
        self._kms = self._session.client('kms')

    def encrypt(self, key_id, text):
        res = self._kms.encrypt(KeyId=key_id, Plaintext=text)
        return base64.b64encode(res.get('CiphertextBlob'))

    def decrypt(self, cipher_text):
        res = self._kms.decrypt(CiphertextBlob=base64.b64decode(cipher_text))
        return res.get('Plaintext')
