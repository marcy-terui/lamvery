# -*- coding: utf-8 -*-

import botocore
import json

from lamvery.clients.base import BaseClient


class ApiGatewayClient(BaseClient):

    def __init__(self, *args, **kwargs):
        super(ApiGatewayClient, self).__init__(*args, **kwargs)
        self._api = self._session.client('apigateway')

    def get_rest_api(self, api_id):
        if api_id is None:
            return None

        try:
            return self._api.get_rest_api(restApiId=api_id)
        except botocore.exceptions.ClientError:
            return None

    def get_export(self, api_id, stage):
        if api_id is None:
            return {}

        try:
            ret = self._api.get_export(
                restApiId=api_id,
                stageName=stage,
                exportType='swagger',
                parameters={'extensions': 'integrations'})
            return json.loads(ret['body'].read())

        except botocore.exceptions.ClientError:
            return {}

    def import_rest_api(self, api_conf):
        return self._api.import_rest_api(body=json.dumps(api_conf))

    def put_rest_api(self, api_id, api_conf):
        return self._api.put_rest_api(
            restApiId=api_id,
            mode='overwrite',
            body=json.dumps(api_conf))

    def delete_rest_api(self, api_id):
        self._api.delete_rest_api(api_id)

    def create_deployment(self, api_id, stage):
        return self._api.create_deployment(
            restApiId=api_id,
            stageName=stage)
