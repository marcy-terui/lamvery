# -*- coding: utf-8 -*-

import boto3
import botocore
import base64

class Client:

    def __init__(self, region=None, profile=None):
        session = boto3.session.Session(
            profile_name=profile, region_name=region)
        self._lambda = session.client('lambda')
        self._kms = session.client('kms')

    def get_function_conf(self, name):
        try:
            res = self._lambda.get_function(
                FunctionName=name)
            return res['Configuration']
        except botocore.exceptions.ClientError:
            return {}

    def create_function(self, zipfile, conf, publish):
        self._lambda.create_function(
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
        self._lambda.update_function_code(
            FunctionName=conf['name'],
            ZipFile=zipfile.read(),
            Publish=publish,
        )

    def update_function_conf(self, conf):
        self._lambda.update_function_configuration(
            FunctionName=conf['name'],
            Role=conf['role'],
            Handler=conf['handler'],
            Description=conf['description'],
            Timeout=conf['timeout'],
            MemorySize=conf['memory_size'],
        )

    def get_alias(self, function, alias):
        try:
            return self._lambda.get_alias(
                FunctionName=function,
                Name=alias)
        except botocore.exceptions.ClientError:
            return {}

    def create_alias(self, function, alias, version):
        self._lambda.create_alias(
                FunctionName=function,
                Name=alias,
                FunctionVersion=version)

    def update_alias(self, function, alias, version):
        self._lambda.update_alias(
                FunctionName=function,
                Name=alias,
                FunctionVersion=version)

    def encrypt(self, key_id, text):
        res = self._kms.encrypt(KeyId=key_id, Plaintext=text)
        return base64.b64encode(res.get('CiphertextBlob'))

    def decrypt(self, cipher_text):
        res = self._kms.decrypt(CiphertextBlob=base64.b64decode(cipher_text))
        return res.get('Plaintext')

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
