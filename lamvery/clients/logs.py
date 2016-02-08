# -*- coding: utf-8 -*-

from lamvery.clients.base import BaseClient


class LogsClient(BaseClient):

    def __init__(self, *args, **kwargs):
        super(LogsClient, self).__init__(*args, **kwargs)
        self._logs = self._session.client('logs')

    def get_log_events(self, function, start, pattern, next_token=None):
        kwargs = {}
        kwargs['logGroupName'] = '/aws/lambda/{}'.format(function)
        kwargs['startTime'] = start
        kwargs['limit'] = 100

        if pattern is not None:
            kwargs['filterPattern'] = pattern
        if next_token is not None:
            kwargs['nextToken'] = next_token

        log_events = self._logs.filter_log_events(**kwargs)

        ret = log_events['events']
        if 'NextToken' in log_events:
            ret.extend(
                self.get_log_events(
                    function, start, pattern, log_events['NextToken']))
        return ret
