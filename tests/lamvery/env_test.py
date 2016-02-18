# -*- coding: utf-8 -*-

import os

from unittest import TestCase
from nose.tools import eq_
import lamvery.env

ENV_JSON = '''
{
    "foo": "bar",
    "baz": "qux"
}
'''


class FunctionsTestCase(TestCase):

    def setUp(self):
        open(lamvery.env.ENV_FILE_NAME, 'w').write(ENV_JSON)
        if 'foo' in os.environ:
            del os.environ['foo']

    def tearDown(self):
        os.remove(lamvery.env.ENV_FILE_NAME)

    def test_load(self):
        lamvery.env.load()
        eq_(os.environ.get('foo'), 'bar')

    def test_load_invalid(self):
        open(lamvery.env.ENV_FILE_NAME, 'w').write('foo')
        lamvery.env.load()
        eq_(os.environ.get('foo'), None)
