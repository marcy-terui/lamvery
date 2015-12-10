# -*- coding: utf-8 -*-

import sys
import argparse
import lamvery
from termcolor import cprint, colored
from lamvery.actions import *

def init(args):
    InitAction(args).action()

def archive(args):
    ArchiveAction(args).action()

def deploy(args):
    DeployAction(args).action()

def decrypt(args):
    DecryptAction(args).action()

def encrypt(args):
    EncryptAction(args).action()

def set_alias(args):
    SetAliasAction(args).action()

def main():
    a_args = ('-a', '--alias',)
    a_kwargs = {
        'help': 'Alias for a version of the function',
        'default': None
    }
    c_args = ('-c', '--conf-file',)
    c_kwargs = {
        'help': 'Configuration YAML file (default: .lamvery.yml)',
        'default': '.lamvery.yml'
    }
    d_args = ('-d', '--dry-run',)
    d_kwargs = {
        'help': 'Dry run',
        'action': 'store_true',
        'default': False
    }
    n_args = ('-n', '--secret-name',)
    n_kwargs = {
        'help': 'The name of the secret value',
        'default': None
    }
    p_args = ('-p', '--publish')
    p_kwargs = {
        'help': 'Publish the version as an atomic operation',
        'action': 'store_true',
        'default': False
    }
    s_args = ('-s', '--store',)
    s_kwargs = {
        'help': 'Store encripted value to configuration file (default: .lamvery.yml)',
        'action': 'store_true',
        'default': False
    }
    v_args = ('-v', '--alias-version',)
    v_kwargs = {
        'help': 'Version of the function to set the alias',
        'default': None
    }

    parser = argparse.ArgumentParser(
        description='Yet another deploy tool for AWS Lambda in the virtualenv environment.',
        epilog='Lamvery version: {}'.format(lamvery.__version__))
    subparsers = parser.add_subparsers(title='subcommands')

    init_parser = subparsers.add_parser(
        'init',
        help='Generate initial configuration file')
    init_parser.add_argument(*c_args, **c_kwargs)
    init_parser.set_defaults(func=init)

    archive_parser = subparsers.add_parser(
        'archive',
        help='Archive your code and libraries to <your-function-name>.zip')
    archive_parser.add_argument(*c_args, **c_kwargs)
    archive_parser.set_defaults(func=archive)

    set_alias_parser = subparsers.add_parser(
        'set-alias',
        help='Set alias to a version of the function')
    set_alias_parser.add_argument(*a_args, **a_kwargs)
    set_alias_parser.add_argument(*c_args, **c_kwargs)
    set_alias_parser.add_argument(*d_args, **d_kwargs)
    set_alias_parser.set_defaults(func=set_alias)

    deploy_parser = subparsers.add_parser(
        'deploy',
        help='Deploy your code and libraries, Update the remote configuration, Set alias (optional)')
    deploy_parser.add_argument(*a_args, **a_kwargs)
    deploy_parser.add_argument(*c_args, **c_kwargs)
    deploy_parser.add_argument(*d_args, **d_kwargs)
    deploy_parser.add_argument(*p_args, **p_kwargs)
    deploy_parser.set_defaults(func=deploy)

    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt a text value using KMS')
    encrypt_parser.add_argument('text', help='The text to be encrypted')
    encrypt_parser.add_argument(*c_args, **c_kwargs)
    encrypt_parser.add_argument(*n_args, **n_kwargs)
    encrypt_parser.add_argument(*s_args, **s_kwargs)
    encrypt_parser.set_defaults(func=encrypt)

    decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt the secret value using KMS')
    decrypt_parser.add_argument(*c_args, **c_kwargs)
    decrypt_parser.add_argument(*n_args, **n_kwargs)
    decrypt_parser.set_defaults(func=decrypt)

    try:
        args = parser.parse_args()
        args.func(args)
        sys.exit(0)
    except Exception as e:
        msg = str(e)
        logging.exception(msg)
        sys.exit(colored(msg, 'red'))
