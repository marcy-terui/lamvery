# -*- coding: utf-8 -*-

import re
import shlex

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
