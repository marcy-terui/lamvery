# -*- coding: utf-8 -*-

import os
import yaml
import tempfile

from unittest import TestCase
from nose.tools import ok_, eq_, raises
from mock import Mock,MagicMock,patch
import lamvery.secret

SECRET_YAML = '''
cipher_texts:
  foo: 1
  bar: 2
'''

class FunctionsTestCase(TestCase):

    def setUp(self):
        open(lamvery.secret.SECRET_FILE_NAME, 'w').write(SECRET_YAML)

    def tearDown(self):
        os.remove(lamvery.secret.SECRET_FILE_NAME)

    def test_generate(self):
        lamvery.secret.generate(
            lamvery.secret.SECRET_FILE_NAME, {'foo': 2, 'bar': 3})
        data = yaml.load(open(lamvery.secret.SECRET_FILE_NAME, 'r').read())
        eq_(data.get('foo'), 2)

    def test_get(self):
        with patch('lamvery.secret.Client') as c:
            class Dummy:
                def decrypt(self, foo):
                    return 'test'
            c.return_value = Dummy()
            eq_(lamvery.secret.get('hoge'), None)
            eq_(lamvery.secret.get('foo'), 'test')
