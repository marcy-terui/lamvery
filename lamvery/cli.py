# -*- coding: utf-8 -*-

import sys
import argparse
import logging
import lamvery
from termcolor import cprint, colored
from lamvery.actions import Actions


def action(args):

    print(args)

    is_dry_msg = ''
    if args.dry_run:
        is_dry_msg = '(Dry run)'

    actions = Actions(args)
    if args.command == 'init':
        cprint('Start initialization...', 'blue', attrs=['bold'])
        actions.init()
    elif args.command == 'archive':
        cprint('Start archiving...', 'blue', attrs=['bold'])
        actions.archive()
    elif args.command == 'deploy':
        cprint('Start deployment...{}'.format(is_dry_msg), 'blue', attrs=['bold'])
        actions.deploy()
    elif args.command == 'set-alias':
        cprint('Start alias setting...{}'.format(is_dry_msg), 'blue', attrs=['bold'])
        actions.set_alias()
    else:
        raise Exception("'{}' command is not exist.".format(args.command))


def main():
    parser = argparse.ArgumentParser(
        description='Yet another deploy tool for AWS Lambda in the virtualenv environment.',
        epilog='Lamvery version: {}'.format(lamvery.__version__))

    parser.add_argument(
        '-c', '--conf-file',
        help='Configuration YAML file (default: lamvery.yml)',
        default='lamvery.yml')
    parser.add_argument(
        '-d', '--dry-run',
        help='Dry run', action='store_true', default=False)
    parser.add_argument(
        '-p', '--publish',
        help='Publish the version as an atomic operation', action='store_true', default=False)
    parser.add_argument(
        '-v', '--alias-version',
        help='Version of the function to set the alias', default=None)

    subparsers = parser.add_subparsers(title='subcommands')

    init_parser = subparsers.add_parser(
        'init',
        help='Generate initial configuration file')

    archive_parser = subparsers.add_parser(
        'archive',
        help='Archive your code and libraries to <your-function-name>.zip')

    alias_parser = subparsers.add_parser(
        'set-alias',
        help='Set alias to a version of the function')
    alias_parser.add_argument(
        '-a', '--alias',
        help='Alias for a version of the function',
        default=None)

    deploy_parser = subparsers.add_parser(
        'deploy',
        help='Deploy your code and libraries, Update the remote configuration, Set alias (optional)')
    deploy_parser.add_argument(
        '-a', '--alias',
        help='Alias for a version of the function',
        default=None)

    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt a text value using KMS')
    encrypt_parser.add_argument('plaintext', help='The text to be encrypted')
    encrypt_parser.add_argument(
        '-n', '--name',
        help='The name for specifying the decoded data on lambda function',
        default=None)
    encrypt_parser.add_argument(
        '-s', '--store',
        help='Store encripted value to configuration file (default: lamvery.yml)',
        action='store_ltrue', default=False)

    try:
        action(parser.parse_args())
        sys.exit(0)
    except Exception as e:
        msg = str(e)
        logging.exception(msg)
        sys.exit(colored(msg, 'red'))
