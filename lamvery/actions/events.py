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
        client = self.get_client()
        func_name = self._config.get_function_name()
        conf = client.get_function_conf(func_name)

        if len(conf) == 0:
            msg = '"{}" function is not exists. Please `deploy` at first.'.format(func_name)
            raise Exception(msg)

        arn = conf['FunctionArn']
        local_rules = self._config.get_events()
        remote_rules = client.get_rules_by_target(arn)

        self._clean(remote_rules, local_rules, arn, func_name)
        self._put_rules(remote_rules, local_rules, func_name)
        self._put_targets(local_rules, arn)

    def _put_rules(self, remote, local, function):
        client = self.get_client()

        for l in local:
            l['state'] = self._convert_state(l.get('disabled'))

            r = self._search_rule(remote, l['rule'])
            if len(r) == 0:
                self._logger.warn(
                    '[EventRule] Create new event rule "{}"'.format(l['rule']))

            self._print_diff(
                prefix='[EventRule] {}:'.format(l['rule']),
                keys=EVENT_RULE_DIFF_KEYS,
                remote=r, local=l)

            ret = client.put_rule(l)
            client.add_permission(function, l['rule'], ret.get('RuleArn'))

    def _convert_state(self, disabled):
        if disabled:
            return 'DISABLED'
        else:
            return 'ENABLED'

    def _search_rule(self, rules, name):
        for r in rules:
            if name in [r.get('Name'), r.get('rule')]:
                return r
        return {}

    def _exist_rule(self, rules, name):
        return len(self._search_rule(rules, name)) > 0

    def _put_targets(self, local, arn):
        client = self.get_client()

        for l in local:
            targets = client.get_targets_by_rule(l['rule'])

            for lt in l['targets']:
                if 'input' in lt:
                    lt['input'] = json.dumps(lt['input'])

                diff_r = {}
                for rt in targets:
                    if rt['Id'] == lt['id']:
                        diff_r = rt
                        break
                    self._logger.warn(
                        '[EventRule] {}: Add "{}" to targets'.format(l['rule'], lt['id']))

                self._print_diff(
                    prefix='[EventTarget] {}:'.format(lt['id']),
                    keys=EVENT_TARGET_DIFF_KEYS,
                    remote=diff_r, local=lt)

            client.put_targets(
                rule=l['rule'], targets=l['targets'], arn=arn)

    def _exist_target(self, targets, target_id):
        for t in targets:
            if target_id in [t.get('id'), t.get('Id')]:
                return True
        return False

    def _clean(self, remote, local, arn, function):
        client = self.get_client()

        for r in remote:
            targets = client.get_targets_by_rule(r['Name'])
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
                client.remove_targets(r['Name'], target_ids)

            if len(targets) == len(target_ids) and not self._keep_empty:
                self._logger.warn(
                    '[EventRule] Delete the event rule "{}" that does not have any targets'.format(
                        r['Name']))
                client.delete_rule(r['Name'])
                client.remove_permission(function, r['Name'])
