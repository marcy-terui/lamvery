# -*- coding: utf-8 -*-

from lamvery.actions.base import BaseAction

CONF_DIFF_KEYS = [
    ('Runtime', 'runtime',),
    ('Role', 'role',),
    ('Handler', 'handler',),
    ('Description', 'description',),
    ('Timeout', 'timeout',),
    ('MemorySize', 'memory_size',),
]

VPC_DIFF_KEYS = [
    ('SubnetIds', 'subnets',),
    ('SecurityGroupIds', 'security_groups',),
]

class ConfigureAction(BaseAction):

    def __init__(self, args):
        super(ConfigureAction, self).__init__(args)

    def action(self):
        func_name = self._config.get_function_name()
        local_conf = self._config.get_configuration()
        client = self.get_lambda_client()
        remote_conf = client.get_function_conf(func_name)
        vpc_config = self._config.get_vpc_configuration()

        if len(remote_conf) > 0:
            self._print_diff(
                prefix='[Function]',
                remote=remote_conf, local=local_conf, keys=CONF_DIFF_KEYS)

            if vpc_config is not None:
                self._print_diff(
                    prefix='[Function]',
                    remote=remote_conf.get('VpcConfig', {}), local=vpc_config, keys=VPC_DIFF_KEYS)

            client.update_function_conf(local_conf)
        else:
            msg = '"{}" function is not exists. Please `deploy` at first.'.format(func_name)
            raise Exception(msg)
