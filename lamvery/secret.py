# -*- coding: utf-8 -*-

import json
from lamvery.clients.kms import KmsClient

SECRET_FILE_NAME = '.lamvery_secret.json'


def get(name):
    data = json.load(open(SECRET_FILE_NAME, 'r'))
    if 'cipher_texts' not in data:
        return None
    if name not in data['cipher_texts']:
        return None
    client = KmsClient(region=data.get('region'))
    return client.decrypt(data['cipher_texts'].get(name))
