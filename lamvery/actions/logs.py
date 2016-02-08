# -*- coding: utf-8 -*-

import time
import signal

from time import mktime
from parsedatetime import Calendar
from lamvery.actions.base import BaseAction


class LogsAction(BaseAction):

    def __init__(self, args):
        super(LogsAction, self).__init__(args)
        self._follow = args.follow
        self._filter = args.filter
        self._interval = args.interval
        self._exit = False
        self._start = args.start

    def action(self):
        self._logger.info('Start viewing the log events...')

        def _exit(signum, frame):
            self._logger.info('Exit by code {} ...'.format(signum))
            self._exit = True

        signal.signal(signal.SIGTERM, _exit)
        signal.signal(signal.SIGINT, _exit)

        start = time.time()
        if self._start is not None:
            time_struct, _ = Calendar().parse(self._start)
            start = mktime(time_struct)

        start = int(start * 1000)

        client = self.get_logs_client()
        function = self._config.get_function_name()
        event_ids = {}

        while self._exit is False:
            events = client.get_log_events(function, start, self._filter)

            for e in events:
                if e['eventId'] not in event_ids:
                    event_ids[e['eventId']] = None
                    print(e['message'])

                    if e['timestamp'] > start:
                        start = e['timestamp']
                        event_ids = {}

            if not self._follow:
                break

            time.sleep(self._interval)
