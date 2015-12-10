# -*- coding: utf-8 -*-

import yaml
from lamvery.client import Client

SECRET_FILE_NAME = '.lamvery_secret.yml'

def generate(path, secret):
    yaml.dump(
        secret,
        open(path, 'w'),
        default_flow_style=False,
        allow_unicode=True)

def get(name):
    data = yaml.load(open(SECRET_FILE_NAME, 'r').read())
    if 'cipher_texts' not in data:
        return None
    if name not in data['cipher_texts']:
        return None
    client = Client(region=data.get('region'))
    return client.decrypt(data['cipher_texts'].get(name))
