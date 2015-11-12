# -*- coding: utf-8 -*-

import sys
import argparse
import logging
from termcolor import colored
from lamvery.actions import Actions


def action(args):
    actions = Actions(
        conf=args.file,
        dry_run=args.dry_run)
    if args.command == 'init':
        actions.init()
    elif args.command == 'archive':
        actions.archive()
    elif args.command == 'deploy':
        actions.deploy()
    else:
        raise Exception("'{}' command is not exist.".format(args.command))


def main():
    parser = argparse.ArgumentParser(
        description='Yet another deploy tool for AWS Lambda in the virtualenv environment.')
    parser.add_argument(
        'command',
        help='init or archive or deploy')
    parser.add_argument(
        '-d', '--dry-run',
        help='Dry run (for deploy)', action='store_true', default=False)
    parser.add_argument(
        '-f', '--file',
        help='Configuration YAML file (default: lamvery.yml)',
        default='lamvery.yml')
    try:
        action(parser.parse_args())
        sys.exit(0)
    except Exception as e:
        msg = str(e)
        logging.exception(msg)
        sys.exit(colored(msg, 'red'))
