# -*- coding: utf-8 -*-

import os
import yaml
import json
import shutil

from unittest import TestCase
from nose.tools import eq_
from mock import patch
import lamvery.secret

SECRET_FILE = 'secret_files_test.txt'

SECRET_JSON = json.dumps({
    'cipher_texts': {
        'foo': 1,
        'bar': 2
    },
    'secret_files': {
        SECRET_FILE: 1
    }
})

class FunctionsTestCase(TestCase):

    def setUp(self):
        open(lamvery.secret.SECRET_FILE_NAME, 'w').write(SECRET_JSON)

    def tearDown(self):
        os.remove(lamvery.secret.SECRET_FILE_NAME)
        if os.path.exists(lamvery.secret.SECRET_DIR):
            shutil.rmtree(lamvery.secret.SECRET_DIR)

    def test_get(self):
        with patch('lamvery.secret.KmsClient') as c:
            class Dummy:
                def decrypt(self, foo):
                    return 'test'
            c.return_value = Dummy()
            eq_(lamvery.secret.get('hoge'), None)
            eq_(lamvery.secret.get('foo'), 'test')

    def test_file(self):
        with patch('lamvery.secret.KmsClient') as c:
            class Dummy:
                def decrypt(self, foo):
                    return 'test'
            c.return_value = Dummy()
            eq_(lamvery.secret.file(SECRET_FILE), os.path.join(lamvery.secret.SECRET_DIR, SECRET_FILE))
            eq_(open(os.path.join(lamvery.secret.SECRET_DIR, SECRET_FILE), 'r').read(), 'test')

    def test_get_file_path(self):
        eq_(lamvery.secret.get_file_path('hoge'), os.path.join(lamvery.secret.SECRET_DIR, 'hoge'))
