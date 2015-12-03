# -*- coding: utf-8 -*-

import boto3
import botocore

class Client:

    def __init__(self, region=None, profile=None):
        session = boto3.session.Session(
            profile_name=profile, region_name=region)
        self._client = session.client('lambda')

    def get_function_conf(self, name):
        try:
            res = self._client.get_function(
                FunctionName=name)
            return res['Configuration']
        except botocore.exceptions.ClientError:
            return {}

    def create_function(self, zipfile, conf, publish):
        self._client.create_function(
            FunctionName=conf['name'],
            Runtime=conf['runtime'],
            Role=conf['role'],
            Handler=conf['handler'],
            Code={
                'ZipFile': zipfile.read(),
            },
            Description=conf['description'],
            Timeout=conf['timeout'],
            MemorySize=conf['memory_size'],
            Publish=publish,
        )

    def update_function_code(self, zipfile, conf, publish):
        self._client.update_function_code(
            FunctionName=conf['name'],
            ZipFile=zipfile.read(),
            Publish=publish,
        )

    def update_function_conf(self, conf):
        self._client.update_function_configuration(
            FunctionName=conf['name'],
            Role=conf['role'],
            Handler=conf['handler'],
            Description=conf['description'],
            Timeout=conf['timeout'],
            MemorySize=conf['memory_size'],
        )

    def get_alias(self, function, alias):
        try:
            return self._client.get_alias(
                FunctionName=function,
                Name=alias)
        except botocore.exceptions.ClientError:
            return {}

    def create_alias(self, function, alias, version):
        self._client.create_alias(
                FunctionName=function,
                Name=alias,
                FunctionVersion=version)

    def update_alias(self, function, alias, version):
        self._client.update_alias(
                FunctionName=function,
                Name=alias,
                FunctionVersion=version)
