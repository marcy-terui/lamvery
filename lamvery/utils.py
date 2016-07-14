# -*- coding: utf-8 -*-

import os
import sys
import re
import shlex
import subprocess

ENV_PATTERN = re.compile('^(?P<name>[^\s]+)\s*=\s*(?P<value>.+)$')


def previous_alias(alias):
    return '{}-pre'.format(alias)


def parse_env_args(env):
    if not isinstance(env, list):
        return None

    ret = {}
    for e in env:
        matches = ENV_PATTERN.match(e)

        if matches is None:
            raise Exception(
                'The format of "env" option must be "NAME=VALUE": {}'.format(e))

        name = matches.group('name')
        value = matches.group('value')
        k, v = shlex.split('{} {}'.format(name, value))
        ret[k] = v

    return ret


def run_commands(commands, working_dir=os.getcwd()):
    cwd = os.getcwd()
    os.chdir(working_dir)

    for c in commands:
        try:
            subprocess.check_output(
                c, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            os.chdir(cwd)
            raise Exception(e.output)

    os.chdir(cwd)


def confirm_overwrite(path):
    ret = True
    if os.path.exists(path):
        print('Overwrite {}? [y/n]: '.format(path))
        y_n = sys.stdin.readline()
        if not y_n.startswith('y'):
            ret = False
    return ret
