# -*- coding: utf-8 -*-

import sys
import argparse
import lamvery
import logging
from termcolor import colored
from lamvery.actions import (
    InitAction,
    BuildAction,
    ConfigureAction,
    DeployAction,
    DecryptAction,
    EncryptAction,
    EncryptFileAction,
    EventsAction,
    InvokeAction,
    RollbackAction,
    SetAliasAction,
    LogsAction,
    ApiAction,
    GenerateAction
)


def init(args):
    InitAction(args).action()


def build(args):
    BuildAction(args).action()


def configure(args):
    ConfigureAction(args).action()


def deploy(args):
    DeployAction(args).action()


def decrypt(args):
    DecryptAction(args).action()


def encrypt(args):
    EncryptAction(args).action()


def encrypt_file(args):
    EncryptFileAction(args).action()


def events(args):
    EventsAction(args).action()


def generate(args):
    GenerateAction(args).action()


def invoke(args):
    InvokeAction(args).action()


def rollback(args):
    RollbackAction(args).action()


def set_alias(args):
    SetAliasAction(args).action()


def logs(args):
    LogsAction(args).action()


def api(args):
    ApiAction(args).action()


def main():
    alias_args = ('-a', '--alias',)
    alias_kwargs = {
        'help': 'Alias for a version of the function',
        'default': None
    }
    conf_file_args = ('-c', '--conf-file',)
    conf_file_kwargs = {
        'help': 'Configuration YAML file (default: .lamvery.yml)',
        'default': '.lamvery.yml'
    }
    dry_run_args = ('-d', '--dry-run',)
    dry_run_kwargs = {
        'help': 'Dry run',
        'action': 'store_true',
        'default': False
    }
    keep_empty_args = ('-k', '--keep-empty-events',)
    keep_empty_kwargs = {
        'help': 'Keep the event rules that does not have any targets.',
        'action': 'store_true',
        'default': False
    }
    single_file_args = ('-s', '--single-file',)
    single_file_kwargs = {
        'help': 'Only use the main lambda function file',
        'action': 'store_true',
        'default': False
    }
    no_libs_args = ('-l', '--no-libs',)
    no_libs_kwargs = {
        'help': 'Archiving without all libraries',
        'action': 'store_true',
        'default': False
    }
    secret_name_args = ('-n', '--secret-name',)
    secret_name_kwargs = {
        'help': 'The name of the secret value',
        'default': None
    }
    publish_args = ('-p', '--publish')
    publish_kwargs = {
        'help': 'Publish the version as an atomic operation',
        'action': 'store_true',
        'default': False
    }
    store_args = ('-s', '--store',)
    store_kwargs = {
        'help': 'Store encripted value to the configuration file (default: .lamvery.secret.yml)',
        'action': 'store_true',
        'default': False
    }
    version_args = ('-v', '--version',)
    version_kwargs = {
        'help': 'Version of the function',
        'default': None
    }
    follow_args = ('-f', '--follow',)
    follow_kwargs = {
        'help': 'Watch the log events and updates the display (like `tail -f`)',
        'action': 'store_true',
        'default': False
    }
    filter_args = ('-F', '--filter',)
    filter_kwargs = {
        'help': 'Filtering pattern for the log messages',
        'default': None
    }
    interval_args = ('-i', '--interval',)
    interval_kwargs = {
        'help': 'Intervals(seconds) to watch the log events',
        'default': 1
    }
    start_args = ('-s', '--start',)
    start_kwargs = {
        'help': 'Time to start the log events watching',
        'default': None
    }
    target_args = ('-t', '--target',)
    target_kwargs = {
        'help': 'The alias of the version that is targeted for setting alias',
        'default': None
    }
    env_args = ('-e', '--env',)
    env_kwargs = {
        'help': 'Environment variables that pass to the function',
        'action': 'append',
        'default': None
    }
    write_args = ('-w', '--write-id',)
    write_kwargs = {
        'help': 'Write the id of your API to the configuration file (default: .lamvery.api.yml)',
        'action': 'store_true',
        'default': False
    }
    stage_args = ('-s', '--stage',)
    stage_kwargs = {
        'help': 'The name of the stage in API Gateway',
        'default': None
    }
    remove_args = ('-r', '--remove',)
    remove_kwargs = {
        'help': 'Remove your API',
        'action': 'store_true',
        'default': False
    }
    no_integrate_args = ('-n', '--no-integrate',)
    no_integrate_kwargs = {
        'help': 'Without automatic integration',
        'action': 'store_true',
        'default': False
    }
    kind_args = ('-k', '--kind',)
    kind_kwargs = {
        'help': 'The kind of the file # accepts "function"',
        'required': True
    }
    filename_args = ('-n', '--name',)
    filename_kwargs = {
        'help': 'The filename to put the decrypted file in the function environment',
        'required': True
    }

    parser = argparse.ArgumentParser(
        description='Yet another deploy tool for AWS Lambda in the virtualenv environment.',
        epilog='Lamvery version: {}'.format(lamvery.__version__))
    subparsers = parser.add_subparsers(title='subcommands')

    init_parser = subparsers.add_parser(
        'init',
        help='Generate initial configuration file')
    init_parser.add_argument(*conf_file_args, **conf_file_kwargs)
    init_parser.set_defaults(func=init)

    build_parser = subparsers.add_parser(
        'build',
        help='Build and archive your code and libraries to <your-function-name>.zip')
    build_parser.add_argument(*conf_file_args, **conf_file_kwargs)
    build_parser.add_argument(*single_file_args, **single_file_kwargs)
    build_parser.add_argument(*no_libs_args, **no_libs_kwargs)
    build_parser.add_argument(*env_args, **env_kwargs)
    build_parser.set_defaults(func=build)

    set_alias_parser = subparsers.add_parser(
        'set-alias',
        help='Set alias to a version of the function')
    set_alias_parser.add_argument(*alias_args, **alias_kwargs)
    set_alias_parser.add_argument(*conf_file_args, **conf_file_kwargs)
    set_alias_parser.add_argument(*dry_run_args, **dry_run_kwargs)
    set_alias_parser.add_argument(*version_args, **version_kwargs)
    set_alias_parser.add_argument(*target_args, **target_kwargs)
    set_alias_parser.set_defaults(func=set_alias)

    configure_parser = subparsers.add_parser(
        'configure',
        help='Update the remote configuration')
    configure_parser.add_argument(*conf_file_args, **conf_file_kwargs)
    configure_parser.add_argument(*dry_run_args, **dry_run_kwargs)
    configure_parser.set_defaults(func=configure)

    deploy_parser = subparsers.add_parser(
        'deploy',
        help='Deploy your code and libraries,' +
             'Update the remote configuration, Set alias (optional)')
    deploy_parser.add_argument(*alias_args, **alias_kwargs)
    deploy_parser.add_argument(*conf_file_args, **conf_file_kwargs)
    deploy_parser.add_argument(*dry_run_args, **dry_run_kwargs)
    deploy_parser.add_argument(*single_file_args, **single_file_kwargs)
    deploy_parser.add_argument(*no_libs_args, **no_libs_kwargs)
    deploy_parser.add_argument(*publish_args, **publish_kwargs)
    deploy_parser.add_argument(*env_args, **env_kwargs)
    deploy_parser.set_defaults(func=deploy)

    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt a text value using KMS')
    encrypt_parser.add_argument('text', help='The text value to encrypt')
    encrypt_parser.add_argument(*conf_file_args, **conf_file_kwargs)
    encrypt_parser.add_argument(*secret_name_args, **secret_name_kwargs)
    encrypt_parser.add_argument(*store_args, **store_kwargs)
    encrypt_parser.set_defaults(func=encrypt)

    decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt the secret value using KMS')
    decrypt_parser.add_argument(*conf_file_args, **conf_file_kwargs)
    decrypt_parser.add_argument(*secret_name_args, **secret_name_kwargs)
    decrypt_parser.set_defaults(func=decrypt)

    encrypt_file_parser = subparsers.add_parser('encrypt-file', help='Encrypt a file using KMS')
    encrypt_file_parser.add_argument('path', help='The file path to encrypt')
    encrypt_file_parser.add_argument(*conf_file_args, **conf_file_kwargs)
    encrypt_file_parser.add_argument(*filename_args, **filename_kwargs)
    encrypt_file_parser.add_argument(*store_args, **store_kwargs)
    encrypt_file_parser.set_defaults(func=encrypt_file)

    decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt the secret value using KMS')
    decrypt_parser.add_argument(*conf_file_args, **conf_file_kwargs)
    decrypt_parser.add_argument(*secret_name_args, **secret_name_kwargs)
    decrypt_parser.set_defaults(func=decrypt)

    events_parser = subparsers.add_parser(
        'events',
        help='Configure all events of CloudWatchEvents using the function')
    events_parser.add_argument(*alias_args, **alias_kwargs)
    events_parser.add_argument(*conf_file_args, **conf_file_kwargs)
    events_parser.add_argument(*dry_run_args, **dry_run_kwargs)
    events_parser.add_argument(*keep_empty_args, **keep_empty_kwargs)
    events_parser.set_defaults(func=events)

    invoke_parser = subparsers.add_parser(
        'invoke',
        help='Invoke the function')
    invoke_parser.add_argument(
        'json', default='{}', help='The JSON string or file that pass to the function')
    invoke_parser.add_argument(*alias_args, **alias_kwargs)
    invoke_parser.add_argument(*conf_file_args, **conf_file_kwargs)
    invoke_parser.add_argument(*version_args, **version_kwargs)
    invoke_parser.set_defaults(func=invoke)

    rollback_parser = subparsers.add_parser(
        'rollback',
        help='Rollback your code and libraries')
    rollback_parser.add_argument(*alias_args, **alias_kwargs)
    rollback_parser.add_argument(*conf_file_args, **conf_file_kwargs)
    rollback_parser.add_argument(*version_args, **version_kwargs)
    rollback_parser.set_defaults(func=rollback)

    logs_parser = subparsers.add_parser(
        'logs',
        help="Watch the function's log events on CloudWatch Logs")
    logs_parser.add_argument(*conf_file_args, **conf_file_kwargs)
    logs_parser.add_argument(*follow_args, **follow_kwargs)
    logs_parser.add_argument(*filter_args, **filter_kwargs)
    logs_parser.add_argument(*interval_args, **interval_kwargs)
    logs_parser.add_argument(*start_args, **start_kwargs)
    logs_parser.set_defaults(func=logs)

    api_parser = subparsers.add_parser(
        'api',
        help='Manage your APIs')
    api_parser.add_argument(*conf_file_args, **conf_file_kwargs)
    api_parser.add_argument(*dry_run_args, **dry_run_kwargs)
    api_parser.add_argument(*no_integrate_args, **no_integrate_kwargs)
    api_parser.add_argument(*remove_args, **remove_kwargs)
    api_parser.add_argument(*stage_args, **stage_kwargs)
    api_parser.add_argument(*write_args, **write_kwargs)
    api_parser.set_defaults(func=api)

    gen_parser = subparsers.add_parser(
        'generate',
        help='Ganerate skeleton files')
    gen_parser.add_argument(*conf_file_args, **conf_file_kwargs)
    gen_parser.add_argument(*kind_args, **kind_kwargs)
    gen_parser.set_defaults(func=generate)

    try:
        args = parser.parse_args()
        args.func(args)
        sys.exit(0)
    except Exception as e:
        logging.exception(e)
        sys.exit(colored(str(e), 'red'))
