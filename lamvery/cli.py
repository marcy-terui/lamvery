# -*- coding: utf-8 -*-

import sys
import argparse
import logging
import lamvery
from termcolor import cprint, colored
from lamvery.actions import Actions


def action(args):

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
        'command',
        help='init or archive or deploy')
    parser.add_argument(
        '-a', '--alias',
        help='Alias for a version of the function',
        default=None)
    parser.add_argument(
        '-c', '--conf-file',
        help='Configuration YAML file (default: lamvery.yml)',
        default='lamvery.yml')
    parser.add_argument(
        '-d', '--dry-run',
        help='Dry run (for deploy)', action='store_true', default=False)
    parser.add_argument(
        '-v', '--alias-version',
        help='Version of the function to set the alias', default=None)
    try:
        action(parser.parse_args())
        sys.exit(0)
    except Exception as e:
        msg = str(e)
        logging.exception(msg)
        sys.exit(colored(msg, 'red'))
