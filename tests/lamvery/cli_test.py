# -*- coding: utf-8 -*-

import os
import sys
import botocore

from unittest import TestCase
from nose.tools import ok_, eq_, raises
from mock import Mock,MagicMock,patch
from lamvery.cli import *

class CliTestCase(TestCase):

    def test_action(self):
        with patch('lamvery.cli.Actions'):
            args = Mock()
            args.file = '/foo/bar'
            args.dry_run = True
            args.command = 'init'
            action(args)
            args.command = 'archive'
            action(args)
            args.command = 'deploy'
            action(args)

    @raises(Exception)
    def test_action_command_not_exists(self):
        with patch('lamvery.cli.Actions'):
            args = Mock()
            args.file = '/foo/bar'
            args.dry_run = True
            args.command = 'foo'
            action(args)

    @patch('argparse.ArgumentParser')
    @patch('sys.exit')
    @patch('lamvery.cli.action')
    def test_main(self, argp, ex, act):
        argp.parse_args = Mock(side_effect=Exception)
        main()

    @patch('argparse.ArgumentParser')
    @patch('sys.exit')
    @patch('lamvery.cli.action')
    def test_main_error(self, argp, ex, act):
        main()
