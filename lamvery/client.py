# -*- coding: utf-8 -*-

import boto3
import botocore
import base64
import hashlib
import json

class Client:

    def __init__(self, region=None, profile=None, dry_run=False):
        session = boto3.session.Session(
            profile_name=profile, region_name=region)
        self._lambda = session.client('lambda')
        self._kms = session.client('kms')
        self._events = session.client('events')
        self._dry_run = dry_run

    def get_function_conf(self, name):
        try:
            res = self._lambda.get_function(
                FunctionName=name)
            return res['Configuration']
        except botocore.exceptions.ClientError:
            return {}

    def create_function(self, zipfile, conf, publish):
        if not self._dry_run:
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
        if not self._dry_run:
            self._lambda.update_function_code(
                FunctionName=conf['name'],
                ZipFile=zipfile.read(),
                Publish=publish,
            )

    def update_function_conf(self, conf):
        if not self._dry_run:
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

    def get_rules_by_target(self, arn):
        names = self._get_rule_names_by_tagert(arn=arn)

        rules = []
        for name in names:
            rules.append(self._events.describe_rule(Name=name))

        return rules

    def _get_rule_names_by_tagert(self, arn, next_token=None):
        try:
            if next_token:
                names = self._events.list_rule_names_by_target(
                    TargetArn=arn, NextToken=next_token, Limit=100)
            else:
                names = self._events.list_rule_names_by_target(
                    TargetArn=arn, Limit=100)
        except botocore.exceptions.ClientError:
            return []

        ret = names['RuleNames']
        if 'NextToken' in names:
            return ret.extend(
                self._get_rule_names_by_tagert(
                    arn=arn, next_token=names['NextToken']))
        else:
            return ret

    def put_rule(self, rule):
        if self._dry_run:
            return {}
        else:
            kwargs = {}
            kwargs['Name'] = rule['rule']
            kwargs['State'] = rule.get('state', 'ENABLED')

            if rule.get('description') is not None:
                kwargs['Description'] = rule.get('description')
            if rule.get('pattern') is not None:
                kwargs['EventPattern'] = rule.get('pattern')
            if rule.get('schedule') is not None:
                kwargs['ScheduleExpression'] = rule.get('schedule')

            return self._events.put_rule(**kwargs)

    def put_targets(self, rule, targets, arn):
        if not self._dry_run:
            t_args = []

            for t in targets:
                arg = {'Id': t['id'], 'Arn': arn}
                if t.get('input') is not None:
                    arg['Input'] = t['input']
                if t.get('input_path') is not None:
                    arg['InputPath'] = t['input_path']
                t_args.append(arg)

            self._events.put_targets(Rule=rule, Targets=t_args)

    def get_targets_by_rule(self, rule, next_token=None):
        try:
            if next_token:
                rules = self._events.list_targets_by_rule(
                    Rule=rule, NextToken=next_token, Limit=100)
            else:
                rules = self._events.list_targets_by_rule(
                    Rule=rule, Limit=100)
        except botocore.exceptions.ClientError:
            return []

        ret = rules['Targets']
        if 'NextToken' in rules:
            return ret.extend(
                self.get_targets_by_rule(
                    rule=rule, next_token=rules['NextToken']))
        else:
            return ret

    def remove_targets(self, rule, targets):
        if not self._dry_run:
            self._events.remove_targets(Rule=rule, Ids=targets)

    def delete_rule(self, name):
        if not self._dry_run:
            self._events.delete_rule(Name=name)

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
