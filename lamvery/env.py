# -*- coding: utf-8 -*-

import json
import os

ENV_FILE_NAME = '.lamvery_env.json'


def load():
    try:
        env = json.load(open(ENV_FILE_NAME, 'r'))
        for k, v in env.items():
            os.environ.setdefault(k, v)

    except:
        pass
