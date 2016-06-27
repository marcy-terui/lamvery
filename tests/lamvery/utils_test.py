# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import eq_, raises
from mock import Mock, patch

from lamvery.utils import (
    previous_alias,
    parse_env_args,
    confirm_overwrite
)


class UtilsActionTestCase(TestCase):

    def test_previous_alias(self):
        eq_(previous_alias('foo'), 'foo-pre')

    def test_parse_env_args(self):
        eq_(parse_env_args('foo'), None)
        eq_(parse_env_args(['foo=bar']), {'foo': 'bar'})
        eq_(parse_env_args(['foo="bar"']), {'foo': 'bar'})
        eq_(parse_env_args(['foo=\'bar baz\'']), {'foo': 'bar baz'})

    @raises(Exception)
    def test_parse_env_args_invalid(self):
        parse_env_args(['foobar'])

    def test_confirm_overwrite(self):
        with patch('sys.stdin') as r:
            # Overwrite yes
            r.readline = Mock(return_value='y')
            eq_(confirm_overwrite('.lamvery.yml'), True)
            # Overwrite no
            r.readline = Mock(return_value='n')
            eq_(confirm_overwrite('.lamvery.yml'), False)
