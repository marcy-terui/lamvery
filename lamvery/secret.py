# -*- coding: utf-8 -*-

import json
import os
from lamvery.clients.kms import KmsClient

SECRET_FILE_NAME = '.lamvery_secret.json'
SECRET_DIR = '/tmp/.lamvery-secret'


def get(name):
    data = json.load(open(SECRET_FILE_NAME, 'r'))
    if 'cipher_texts' not in data:
        return None
    if name not in data['cipher_texts']:
        return None
    client = KmsClient(region=data.get('region'))
    return client.decrypt(data['cipher_texts'].get(name))


def file(filename):
    data = json.load(open(SECRET_FILE_NAME, 'r'))
    secret_files = data.get('secret_files', {})
    client = KmsClient(region=data.get('region'))

    if not os.path.exists(SECRET_DIR):
        os.mkdir(SECRET_DIR)

    if filename not in secret_files:
        return None

    p = os.path.join(SECRET_DIR, filename)
    if not os.path.exists(p):
        with open(p, 'w') as f:
            f.write(client.decrypt(secret_files[filename]))

    return p


def get_file_path(filename):
    return os.path.join(SECRET_DIR, filename)
