# -*- coding: utf-8 -*-

import json
from lamvery.actions.base import BaseAction

EVENT_RULE_DIFF_KEYS = [
    ('Description', 'description',),
    ('EventPattern', 'pattern',),
    ('RoleArn', 'role',),
    ('ScheduleExpression', 'schedule',),
    ('State', 'state',),
]

EVENT_TARGET_DIFF_KEYS = [
    ('Input', 'input',),
    ('InputPath', 'input_path',),
]


class EventsAction(BaseAction):

    def __init__(self, args):
        super(EventsAction, self).__init__(args)
        self._keep_empty = args.keep_empty_events

    def action(self):
        lambda_client = self.get_lambda_client()
        events_client = self.get_events_client()
        func_name = self._config.get_function_name()
        alias_name = self.get_alias_name()
        conf = lambda_client.get_function_conf(func_name, alias_name)

        if len(conf) == 0:
            msg = '"{}" function does not exist. Please `deploy` first.'.format(func_name)
            raise Exception(msg)

        arn = conf['FunctionArn']
        local_rules = self._config.get_events().get('rules')
        remote_rules = events_client.get_rules_by_target(arn)

        self._clean(remote_rules, local_rules, arn, func_name, alias_name)
        self._put_rules(remote_rules, local_rules, func_name, alias_name)
        self._put_targets(local_rules, arn)

    def _put_rules(self, remote, local, function, alias):
        lambda_client = self.get_lambda_client()
        events_client = self.get_events_client()

        for l in local:
            l['state'] = self._convert_state(l.get('disabled'))

            r = self._search_rule(remote, l['name'])
            if len(r) == 0:
                self._logger.warn(
                    '[EventRule] Create new event rule "{}"'.format(l['name']))

            self._print_diff(
                prefix='[EventRule] {}:'.format(l['name']),
                keys=EVENT_RULE_DIFF_KEYS,
                remote=r, local=l)

            ret = events_client.put_rule(l)
            lambda_client.add_permission(function, alias, l['name'], ret.get('RuleArn'))

    def _convert_state(self, disabled):
        if disabled:
            return 'DISABLED'
        else:
            return 'ENABLED'

    def _search_rule(self, rules, name):
        for r in rules:
            if name in [r.get('Name'), r.get('name')]:
                return r
        return {}

    def _exist_rule(self, rules, name):
        return len(self._search_rule(rules, name)) > 0

    def _put_targets(self, local, arn):
        client = self.get_events_client()

        for l in local:
            targets = client.get_targets_by_rule(l['name'])

            for lt in l['targets']:
                if 'input' in lt:
                    lt['input'] = json.dumps(lt['input'])

                diff_r = {}
                for rt in targets:
                    if rt['Id'] == lt['id']:
                        diff_r = rt
                        break
                    self._logger.warn(
                        '[EventRule] {}: Add "{}" to targets'.format(l['name'], lt['id']))

                self._print_diff(
                    prefix='[EventTarget] {}:'.format(lt['id']),
                    keys=EVENT_TARGET_DIFF_KEYS,
                    remote=diff_r, local=lt)

            client.put_targets(
                rule=l['name'], targets=l['targets'], arn=arn)

    def _exist_target(self, targets, target_id):
        for t in targets:
            if target_id in [t.get('id'), t.get('Id')]:
                return True
        return False

    def _clean(self, remote, local, arn, function, alias):
        lambda_client = self.get_lambda_client()
        events_client = self.get_events_client()

        for r in remote:
            targets = events_client.get_targets_by_rule(r['Name'])
            target_ids = []

            l = self._search_rule(local, r['Name'])

            for rt in targets:
                msg = '[EventRule] {}: Remove undifined event target "{}"'.format(
                    r['Name'], rt['Id'])
                if len(l) > 0:
                    if not self._exist_target(l['targets'], rt['Id']):
                        self._logger.warn(msg)
                        target_ids.append(rt['Id'])
                elif rt['Arn'] == arn:
                    self._logger.warn(msg)
                    target_ids.append(rt['Id'])

            if len(target_ids) > 0:
                events_client.remove_targets(r['Name'], target_ids)

            if len(targets) == len(target_ids) and not self._keep_empty:
                self._logger.warn(
                    '[EventRule] Delete the event rule "{}" that does not have any targets'.format(
                        r['Name']))
                events_client.delete_rule(r['Name'])
                lambda_client.remove_permission(function, alias, r['Name'])
