# -*- coding: utf-8 -*-

import json
from lamvery.client import Client

SECRET_FILE_NAME = '.lamvery_secret.json'


def generate(path, secret):
    json.dump(
        secret,
        open(path, 'w'))


def get(name):
    data = json.load(open(SECRET_FILE_NAME, 'r'))
    if 'cipher_texts' not in data:
        return None
    if name not in data['cipher_texts']:
        return None
    client = Client(region=data.get('region'))
    return client.decrypt(data['cipher_texts'].get(name))
