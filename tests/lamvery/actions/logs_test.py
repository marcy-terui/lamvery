# -*- coding: utf-8 -*-

import time

from unittest import TestCase
from nose.tools import raises
from mock import Mock, patch

from lamvery.actions.logs import LogsAction


def default_args():
    args = Mock()
    args.conf_file = '.lamvery.yml'
    args.follow = False
    args.interval = 1
    args.start = '-1h'
    return args


class LogsActionTestCase(TestCase):

    def test_action(self):
        c = Mock()
        c.get_log_events = Mock(
            return_value=[{'message': 'foo', 'eventId': 'bar', 'timestamp': int(time.time() * 1000)}])

        action = LogsAction(default_args())
        action._get_client = Mock(return_value=c)
        action.action()
