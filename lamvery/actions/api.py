# -*- coding: utf-8 -*-

import json
import re
import hashlib

from datetime import datetime
from datadiff import diff
from lamvery.actions.base import BaseAction
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter

DEFAULT_MAPPING_TEMPLATE = '''
##  See http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-mapping-template-reference.html
##  This template will pass through all parameters including path, querystring, header, stage variables,
##  and context through to the integration endpoint via the body/payload
#set($allParams = $input.params())
{
"body-json" : "$input.json('$')",
"params" : {
#foreach($type in $allParams.keySet())
    #set($params = $allParams.get($type))
"$type" : {
    #foreach($paramName in $params.keySet())
    "$paramName" : "$util.escapeJavaScript($params.get($paramName))"
        #if($foreach.hasNext),#end
    #end
}
    #if($foreach.hasNext),#end
#end
},
"stage-variables" : {
#foreach($key in $stageVariables.keySet())
"$key" : "$util.escapeJavaScript($stageVariables.get($key))"
    #if($foreach.hasNext),#end
#end
},
"context" : {
    "account-id" : "$context.identity.accountId",
    "api-id" : "$context.apiId",
    "api-key" : "$context.identity.apiKey",
    "authorizer-principal-id" : "$context.authorizer.principalId",
    "caller" : "$context.identity.caller",
    "cognito-authentication-provider" : "$context.identity.cognitoAuthenticationProvider",
    "cognito-authentication-type" : "$context.identity.cognitoAuthenticationType",
    "cognito-identity-id" : "$context.identity.cognitoIdentityId",
    "cognito-identity-pool-id" : "$context.identity.cognitoIdentityPoolId",
    "http-method" : "$context.httpMethod",
    "stage" : "$context.stage",
    "source-ip" : "$context.identity.sourceIp",
    "user" : "$context.identity.user",
    "user-agent" : "$context.identity.userAgent",
    "user-arn" : "$context.identity.userArn",
    "request-id" : "$context.requestId",
    "resource-id" : "$context.resourceId",
    "resource-path" : "$context.resourcePath"
    }
}
'''


class ApiAction(BaseAction):

    def __init__(self, args):
        super(ApiAction, self).__init__(args)
        self._no_integrate = args.no_integrate
        self._remove = args.remove
        self._write_id = args.write_id
        self._stage = args.stage

    def get_stage_name(self):
        if self._stage is not None:
            return self._stage
        else:
            return self._config.get_api_stage()

    def get_cors(self):
        cors = self._config.get_api_cors()
        if cors is not None:
            cors['origin'] = "'{}'".format(cors['origin'])
            cors['methods'] = "'{}'".format(','.join(cors['methods']))
            cors['headers'] = "'{}'".format(','.join(cors['headers']))
        return cors

    def action(self):
        client = self.get_apigateway_client()
        api_id = self._config.get_api_id()
        stage = self.get_stage_name()
        cors = self.get_cors()
        api_conf = self._config.get_api_configuration()

        if not self._no_integrate:
            api_conf = self._integrate_aws(api_conf, stage, cors)

        self._print_conf_diff(
            api_conf, self._get_remote_configuration(client, api_id, stage))

        if not self._dry_run:
            ret = self._apply_api(client, api_id, api_conf)
            if api_id is None:
                api_id = ret['id']

            if self._write_id:
                self._config.save_api_id(ret['id'])

            self._add_permissions(api_id, api_conf)

            self._print_apply_result(ret)
            ret = self._deploy(client, ret['id'], stage)
            self._print_deploy_result(ret)

    def _add_permissions(self, api_id, api_conf):
        client = self.get_lambda_client()

        for path, methods in api_conf['paths'].items():
            for method in methods.keys():
                client.add_permission(
                    self._config.get_function_name(),
                    self.get_alias_name(),
                    hashlib.md5(api_id + method + path).hexdigest(),
                    'arn:aws:execute-api:{}:{}:{}/*/{}{}'.format(
                        client._session.region_name,
                        client.get_account_id(),
                        api_id,
                        method.upper(),
                        path),
                    'apigateway.amazonaws.com')

    def _get_remote_configuration(self, client, api_id, stage):
        if api_id is None:
            return {}
        return client.get_export(api_id, stage)

    def _integrate_aws(self, api_conf, stage, cors):
        client = self.get_lambda_client()
        api_conf['basePath'] = '/{}'.format(stage)
        api_conf['info']['version'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        for path, methods in api_conf['paths'].items():

            for method, conf in methods.items():
                conf.setdefault('x-amazon-apigateway-integration', {})
                integration = conf['x-amazon-apigateway-integration']
                integration.setdefault('type', 'aws')
                integration.setdefault('httpMethod', 'POST')

                uri = 'arn:aws:apigateway:{}:lambda:path/2015-03-31/functions/'.format(
                    client._session.region_name)
                uri += '{}/invocations'.format(client.get_function_conf(
                    self._config.get_function_name(),
                    self.get_alias_name()).get('FunctionArn'))

                integration.setdefault('uri', uri)
                integration.setdefault(
                    'requestTemplates',
                    {'application/json': DEFAULT_MAPPING_TEMPLATE})

                for code in conf['responses'].keys():
                    integration.setdefault('responses', {
                        'default': {
                            'statusCode': str(code)
                        }
                    })

                    if cors is not None:
                        conf['responses'][code].setdefault('headers', {
                            'Access-Control-Allow-Origin': {'type': 'string'}
                        })

                if cors is not None:
                    integration['responses']['default'].setdefault(
                        'responseParameters', self._generate_method_cors(cors))

                    api_conf['paths'][path].setdefault(
                        'options',
                        self._generate_option_cors(cors))

                conf['x-amazon-apigateway-integration'] = integration
                api_conf['paths'][path][method] = conf

        return api_conf

    def _generate_method_cors(self, cors):
        return {
            'method.response.header.Access-Control-Allow-Origin': cors.get('origin')
        }

    def _generate_option_cors(self, cors):
        return {
            'consumes': ['application/json'],
            'produces': ['application/json'],
            'responses': {
                200: {
                    'description': '200 response',
                    'headers': {
                        'Access-Control-Allow-Origin': {'type': 'string'},
                        'Access-Control-Allow-Methods': {'type': 'string'},
                        'Access-Control-Allow-Headers': {'type': 'string'},
                    }
                }
            },
            'x-amazon-apigateway-integration': {
                'responses': {
                    'default': {
                        'statusCode': '200',
                        'responseParameters': {
                            'method.response.header.Access-Control-Allow-Methods': cors.get('methods'),
                            'method.response.header.Access-Control-Allow-Headers': cors.get('headers'),
                            'method.response.header.Access-Control-Allow-Origin': cors.get('origin'),
                        }
                    }
                },
                'requestTemplates': {
                    'application/json': '{"statusCode": 200}'
                },
                'type': 'mock'
            }
        }

    def _apply_api(self, client, api_id, api_conf):
        api = client.get_rest_api(api_id)
        ret = None

        if api is None:
            if self._remove:
                self._logger.info('"{}" is not exists.'.format(api_id))
            else:
                self._logger.info('[API] Add new rest api.')
                ret = client.import_rest_api(api_conf)
        else:
            if self._remove:
                self._logger.warn('[API] Delete rest api "{}".'.format(api_id))
                client.delete_rest_api(api_id)
            else:
                self._logger.info('[API] Update rest api "{}".'.format(api_id))
                ret = client.put_rest_api(api_id, api_conf)

        return ret

    def _print_apply_result(self, ret):
        if ret is not None:

            self._logger.info('[API] ID: {}'.format(ret['id']))
            self._logger.info('[API] Name: {}'.format(ret['name']))
            self._logger.info('[API] Description: {}'.format(ret.get('description')))

            for w in ret.get('warnings', []):
                self._logger.warn('[API] Warning: "{}".'.format(w))

    def _deploy(self, client, api_id, stage):
        return client.create_deployment(api_id, stage)

    def _print_deploy_result(self, ret):
        if ret is not None:
            self._logger.info('[API] Deployment ID: {}'.format(ret['id']))
            self._logger.info('[API] Deployment description: {}'.format(ret.get('description')))
            self._logger.info('[API] Deployment API Summary: {}'.format(ret.get('apiSummary')))

    def _print_conf_diff(self, local, remote):
        str_diff = diff(remote, json.loads(json.dumps(local))).__str__()
        str_diff = re.compile(r'^( +)([\-\+])', re.MULTILINE).sub(r'\2\1', str_diff)
        self._logger.warn('[API] Configuration:\n{}'.format(highlight(
            str_diff,
            get_lexer_by_name('diff'),
            TerminalFormatter())))
