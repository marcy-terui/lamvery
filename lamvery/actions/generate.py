# -*- coding: utf-8 -*-

from lamvery.actions.base import BaseAction
from lamvery.utils import confirm_overwrite

PY_CODE = """import lamvery

def {}(event, context):
    # Use environment variables
    # lamvery.env.load()
    # print(os.environ['FOO'])

    # Use KMS encryption
    # print(lamvery.secret.get('foo'))

    print('This is a skeleton function.')
"""

JS_CODE = """var lamvery = require('./lamvery.js');

exports.{} = function(event, context) {{
    // Use environment variables
    // lamvery.env.load();
    // console.log(process.env.FOO);

    // Use KMS encryption
    // lamvery.secret.get('foo', function(err, data) {{
    //     console.log(data);
    // }});

    console.log('This is a skeleton function.');
}}
"""


class GenerateAction(BaseAction):

    def __init__(self, args):
        super(GenerateAction, self).__init__(args)
        self._kind = args.kind

    def action(self):
        if self._kind == 'function':
            self._generate_function(
                self._config.get_handler_namespace(),
                self._config.get_handler_function(),
                self._config.get_runtime())
        else:
            raise Exception('"{}" kind is not supported.'.format(self._kind))

    def _generate_function(self, namespace, function, runtime):
        if 'python' in runtime:
            path = '{}.py'.format(namespace)
            content = PY_CODE.format(function)
        elif 'nodejs' in runtime:
            path = '{}.js'.format(namespace)
            content = JS_CODE.format(function)
        else:
            raise Exception('Runtime "{}" is not supported.'.format(runtime))

        if confirm_overwrite(path):
            open(path, 'w').write(content)
            self._logger.info('Output skeleton function: {}'.format(path))
