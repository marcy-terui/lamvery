# -*- coding: utf-8 -*-

import botocore

from lamvery.clients.base import BaseClient


class EventsClient(BaseClient):

    def __init__(self, *args, **kwargs):
        super(EventsClient, self).__init__(*args, **kwargs)
        self._events = self._session.client('events')

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
            ret.extend(
                self._get_rule_names_by_tagert(
                    arn=arn, next_token=names['NextToken']))
        return ret

    def put_rule(self, rule):
        if self._dry_run:
            return {}
        else:
            kwargs = {}
            kwargs['Name'] = rule['name']
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
            ret.extend(
                self.get_targets_by_rule(
                    rule=rule, next_token=rules['NextToken']))
        return ret

    def remove_targets(self, rule, targets):
        if not self._dry_run:
            self._events.remove_targets(Rule=rule, Ids=targets)

    def delete_rule(self, name):
        if not self._dry_run:
            self._events.delete_rule(Name=name)
