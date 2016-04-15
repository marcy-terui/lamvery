# -*- coding: utf-8 -*-

import boto3

from abc import ABCMeta


class BaseClient:

    __metaclass__ = ABCMeta

    def __init__(self, region=None, profile=None, dry_run=False):
        self._session = boto3.session.Session(
            profile_name=profile, region_name=region)
        self._dry_run = dry_run
        self._sts = self._session.client('sts')

    def get_account_id(self):
        return self._sts.get_caller_identity().get('Account')
