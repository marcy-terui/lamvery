# -*- coding: utf-8 -*-

import botocore
import hashlib

from lamvery.clients.base import BaseClient
from lamvery.utils import previous_alias


class LambdaClient(BaseClient):

    def __init__(self, *args, **kwargs):
        super(LambdaClient, self).__init__(*args, **kwargs)
        self._lambda = self._session.client('lambda')

    def get_function_conf(self, name):
        try:
            res = self._lambda.get_function(
                FunctionName=name)
            return res['Configuration']
        except botocore.exceptions.ClientError:
            return {}

    def create_function(self, zipfile, conf, publish):
        kwargs = {}
        kwargs['FunctionName'] = conf['name']
        kwargs['Runtime'] = conf['runtime']
        kwargs['Role'] = conf['role']
        kwargs['Handler'] = conf['handler']
        kwargs['Code'] = {'ZipFile': zipfile.read()}
        kwargs['Publish'] = publish

        description = conf.get('description')
        if description is not None:
            kwargs['Description'] = description

        timeout = conf.get('timeout')
        if timeout is not None:
            kwargs['Timeout'] = timeout

        memory_size = conf.get('memory_size')
        if memory_size is not None:
            kwargs['MemorySize'] = memory_size

        vpc_config = conf.get('vpc_config')
        if vpc_config is not None:
            kwargs['VpcConfig'] = self._build_vpc_config(vpc_config)

        if not self._dry_run:
            self._lambda.create_function(**kwargs)

    def _build_vpc_config(self, vpc_config):
        return {
            'SubnetIds': vpc_config['subnets'],
            'SecurityGroupIds': vpc_config['security_groups']}

    def update_function_code(self, zipfile, conf, publish):
        if not self._dry_run:
            ret = self._lambda.update_function_code(
                FunctionName=conf['name'],
                ZipFile=zipfile.read(),
                Publish=publish)
            return ret['Version']
        return None

    def update_function_conf(self, conf):
        kwargs = {}
        kwargs['FunctionName'] = conf['name']
        kwargs['Role'] = conf['role']
        kwargs['Handler'] = conf['handler']

        description = conf.get('description')
        if description is not None:
            kwargs['Description'] = description

        timeout = conf.get('timeout')
        if timeout is not None:
            kwargs['Timeout'] = timeout

        memory_size = conf.get('memory_size')
        if memory_size is not None:
            kwargs['MemorySize'] = memory_size

        vpc_config = conf.get('vpc_config')
        if vpc_config is not None:
            kwargs['VpcConfig'] = self._build_vpc_config(vpc_config)

        if not self._dry_run:
            self._lambda.update_function_configuration(**kwargs)

    def get_alias(self, function, alias):
        try:
            return self._lambda.get_alias(
                FunctionName=function,
                Name=alias)
        except botocore.exceptions.ClientError:
            return {}

    def create_alias(self, function, alias, version):
        if not self._dry_run:
            self._lambda.create_alias(
                FunctionName=function,
                Name=alias,
                FunctionVersion=version)

    def update_alias(self, function, alias, version):
        if not self._dry_run:
            self._lambda.update_alias(
                FunctionName=function,
                Name=alias,
                FunctionVersion=version)

    def calculate_capacity(self, next_marker=None):
        if next_marker:
            r = self._lambda.list_functions(MaxItems=500, Marker=next_marker)
        else:
            r = self._lambda.list_functions(MaxItems=500)

        size = sum(
            self._calculate_versions_capacity(
                f['FunctionName']) for f in r['Functions'])

        if 'NextMarker' in r:
            return size + self.calculate_capacity(next_marker=r['NextMarker'])
        else:
            return size

    def _calculate_versions_capacity(self, function_name, next_marker=None):
        if next_marker:
            r = self._lambda.list_versions_by_function(
                FunctionName=function_name, MaxItems=500, Marker=next_marker)
        else:
            r = self._lambda.list_versions_by_function(
                FunctionName=function_name, MaxItems=500)

        size = sum(f['CodeSize'] for f in r['Versions'])

        if 'NextMarker' in r:
            return size + self._calculate_versions_capacity(
                function_name=function_name, next_marker=r['NextMarker'])
        else:
            return size

    def add_permission(self, function, rule_name, rule_arn):
        if not self._dry_run:
            try:
                self._lambda.add_permission(
                    FunctionName=function,
                    Action='lambda:InvokeFunction',
                    Principal='events.amazonaws.com',
                    SourceArn=rule_arn,
                    StatementId=self._generate_statement_id(function, rule_name))
            except botocore.exceptions.ClientError:
                pass

    def remove_permission(self, function, rule):
        if not self._dry_run:
            self._lambda.remove_permission(
                FunctionName=function,
                StatementId=self._generate_statement_id(function, rule))

    def _generate_statement_id(self, function, rule):
        return hashlib.sha256(
            'lamvery-{}-{}'.format(function, rule)).hexdigest()

    def invoke(self, name, qualifier=None, payload=None):
        kwargs = {}
        kwargs['FunctionName'] = name
        kwargs['InvocationType'] = 'RequestResponse'
        kwargs['LogType'] = 'Tail'

        if payload is not None:
            kwargs['Payload'] = payload
        if qualifier is not None:
            kwargs['Qualifier'] = qualifier

        return self._lambda.invoke(**kwargs)

    def get_previous_version(self, function, alias):
        ver = self.get_alias(function, previous_alias(alias))
        return ver.get('FunctionVersion')
