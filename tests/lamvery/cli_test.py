# -*- coding: utf-8 -*-

import os
import sys
import botocore

from unittest import TestCase
from nose.tools import ok_, eq_, raises
from mock import Mock,MagicMock,patch
from lamvery.cli import *

class FunctionsTestCase(TestCase):

    def test_init(self):
        with patch('lamvery.cli.InitAction'):
            init(Mock())

    def test_archive(self):
        with patch('lamvery.cli.ArchiveAction'):
            archive(Mock())

    def test_configure(self):
        with patch('lamvery.cli.ConfigureAction'):
            configure(Mock())

    def test_deploy(self):
        with patch('lamvery.cli.DeployAction'):
            deploy(Mock())

    def test_encrypt(self):
        with patch('lamvery.cli.EncryptAction'):
            encrypt(Mock())

    def test_events(self):
        with patch('lamvery.cli.EventsAction'):
            events(Mock())

    def test_decrypt(self):
        with patch('lamvery.cli.DecryptAction'):
            decrypt(Mock())

    def test_set_alias(self):
        with patch('lamvery.cli.SetAliasAction'):
            set_alias(Mock())

    @patch('argparse.ArgumentParser')
    @patch('sys.exit')
    def test_main(self, argp, ex):
        main()

    @patch('argparse.ArgumentParser')
    @patch('sys.exit')
    def test_main_error(self, argp, ex):
        argp.parse_args = Mock(side_effect=Exception)
        main()
