# -*- coding: utf-8 -*-

from unittest import TestCase
from mock import Mock, patch
from lamvery.cli import (
    main,
    init,
    build,
    configure,
    deploy,
    encrypt,
    events,
    decrypt,
    set_alias,
    invoke,
    rollback,
    api,
    generate
)


class FunctionsTestCase(TestCase):

    def test_init(self):
        with patch('lamvery.cli.InitAction'):
            init(Mock())

    def test_archive(self):
        with patch('lamvery.cli.BuildAction'):
            build(Mock())

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

    def test_invoke(args):
        with patch('lamvery.cli.InvokeAction'):
            invoke(Mock())

    def test_rollback(args):
        with patch('lamvery.cli.RollbackAction'):
            rollback(Mock())

    def test_api(args):
        with patch('lamvery.cli.ApiAction'):
            api(Mock())

    def test_generate(args):
        with patch('lamvery.cli.GenerateAction'):
            generate(Mock())

    @patch('argparse.ArgumentParser')
    @patch('sys.exit')
    def test_main(self, argp, ex):
        main()

    @patch('argparse.ArgumentParser')
    @patch('sys.exit')
    def test_main_error(self, argp, ex):
        argp.parse_args = Mock(side_effect=Exception)
        main()
