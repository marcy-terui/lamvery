Lamvery
=======

[![Build Status](https://img.shields.io/travis/marcy-terui/lamvery/master.svg)](http://travis-ci.org/marcy-terui/lamvery)
[![Coverage](https://img.shields.io/coveralls/marcy-terui/lamvery.svg)](https://coveralls.io/github/marcy-terui/lamvery)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/marcy-terui/lamvery/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/marcy-terui/lamvery/?branch=master)
[![Version](https://img.shields.io/pypi/v/lamvery.svg)](https://pypi.python.org/pypi/lamvery)
[![Downloads](https://img.shields.io/pypi/dm/lamvery.svg)](https://pypi.python.org/pypi/lamvery/)

# Description

User-friendly deploy and management tool for AWS Lambda function.

### Why user-friendly?

#### The format of the configuration file is `YAML`(with `Jinja2`)

- `YAML` is user-friendly than `JSON`
- We can avoid some redundant contents by `Jinja2` template engine

#### Additional features that are not in the standard Lambda functions

- Passing the environment variables
- Passing the confidential informations use `KMS` encryption
- And more

#### More useful features for deploying and invoking our functions

- We can build, configure, deploy, rollback and invoke with a single command
- We can rollback **correctly** to the previous version of the alias
- Deply(build) hooks
- And more

#### More useful features for using and managing the related services

- CloudWatch Events
- CloudWatch Logs
- And more

# Requirements

- Python2.7
- pip

# Recommends

- virtualenv  
**Automatically collect the lightweighted and compiled libraries in the virtualenv environment.**

# Installation

## PyPI

```sh
pip install lamvery
```

## Apt

```sh
echo "deb https://dl.bintray.com/willyworks/deb trusty main" | sudo tee -a /etc/apt/sources.list
sudo apt-get update
sudo apt-get install lamvery
export PATH=/opt/lamvery/bin:$PATH
```

## Yum

```sh
echo "
[bintraybintray-willyworks-rpm]
name=bintray-willyworks-rpm
baseurl=https://dl.bintray.com/willyworks/rpm/centos/\$releaserver/\$basearch/
gpgcheck=0
enabled=1
" | sudo tee -a /etc/yum.repos.d/bintray-willyworks-rpm.repo
sudo yum install lamvery
export PATH=/opt/lamvery/bin:$PATH
```

# Setup and configuration

First,

```sh
lamvery init
```

And then edit your `.lamvery.yml` like so.  
The configuration is written in YAML syntax with `jinja2` template.  
Environment variables are stored in the `env` variable.

## General settings (deafult: `.lamvery.yml`)

```yml
profile: private
region: us-east-1
versioning: true
default_alias: test
clean_build: false
configuration:
  name: lamvery-test
  runtime: python2.7
  role: {{ env['AWS_LAMBDA_ROLE'] }}
  handler: lambda_function.lambda_handler
  description: This is sample lambda function.
  timeout: 10
  memory_size: 128
  vpc_config:
    subnets:
    - subnet-cadf2993
    security_groups:
    - sg-4d095028
```

### profile
The name of a profile to use. If not given, it depends on `boto3`.

### region
The region name of your environment.  
If you doesn't set this option, it depends on `boto3`.

### versioning
Enable the function versioning.

### default_alias
The alias when it has not been specified in the `-a` or `--alias` option.

### clean_build
Build the archive(zip) in the temporary area.

### configuration

- name  
The name of your function.

- runtime  
The runtime environment for the Lambda function you are uploading.  
Currently, `lamvery` supports `python2.7` and `nodejs`.

- role  
The Amazon Resource Name (ARN) of the IAM role for your function.

- handler  
The function within your code that Lambda calls to begin execution.

- description  
The description of your function.

- timeout  
The function execution time(seconds) at which Lambda should terminate the function.

- memory_size  
The amount of memory for your function environment.

- vpc_config  
The VPC configurations for the function to access resources in your VPC.  
  - subnets  
    The Subnet ids in your VPC.  
  - security_groups  
    The SecurityGroup ids in your VPC.  

## CloudWatch Events settings (deafult: `.lamvery.event.yml`)

```yml
rules:
- name: foo
  description: bar
  schedule: 'rate(5 minutes)'
  targets:
  - id: test-target-id
    input:
      this:
      - is: a
      - sample: input
```

### rules
CloudWatch Event Rules.

- NAME  
The name of CloudWatch Event Rule.

- description  
The description of CloudWatch Event Rule.

- schedule  
The schedule expression of CloudWatch Event Rule.

- disabled  
When this setting is true, change the state of CloudWatch Event Rule to `DISABLED`.  
default: `false`

- targets  
The targets of CloudWatch Event Rule.
  - id  
  The unique target assignment ID.
  - input  
  Arguments passed to the target.
  - input_path  
  The value of the JSONPath that is used for extracting part of the matched event when passing it to the target.

*`input` and `input_path` are mutually-exclusive and optional parameters of a target.*

## Secret informations (deafult: `.lamvery.secret.yml`)

```yml
key_id: {{ env['AWS_KMS_KEY_ID'] }}
cipher_texts:
  foo: CiC4xW9lg7HaxaueeN+d9yJMyY1uw1i7tYVvQz9I8+e2UBKXAQEBAgB4uMVvZYOx2sWrnnjfnfciTMmNbsNYu7WFb0M/SPPntlAAAABuMGwGCSqGSIb3DQEHBqBfMF0CAQAwWAYJKoZIhvcNAQcBMB4GCWCGSAFlAwQBLjARBAzWTJWk/69T8NTBquoCARCAK2Hg2de71hzwjiMKkfMSG2G1Olj1EjxajS+3PsFVTPZ91Oi/AjR1aMqAI8U=
```

### key_id  
The ID of your encryption key on KMS.

### cipher_texts  
The name and cipher texts to pass to the lambda function.

## Excluded patterns from the archive (deafult: `.lamvery.exclude.yml`)

```yml
- ^\.lamvery\.yml$
- ^\.lamvery\.event\.yml$
- ^\.lamvery\.secret\.yml$
- ^\.lamvery\.exclude\.yml$
```

Exclude files or directories using regular expression.

## Action hooks (deafult: `.lamvery.hook.yml`)

```yml
build:
  pre:
  - pip install -r requirements.txt -t ./
  post: []
```

### build
The hooks for `build`(and `deploy`)

- pre  
The commands that run before building.

- post  
The commands that run after building.

## API Gateway integration (beta)

```yml
api_id: myipugal74
stage
: dev
cors:
  origin: '*'
  methods:
  - GET
  - OPTION
  headers:
  - Content-Type
  - X-Amz-Date
  - Authorization
  - X-Api-Key
configuration:
  swagger: '2.0'
  info:
    title: Sample API
  schemes:
  - https
  paths:
    /:
      get:
        produces:
        - application/json
        parameters:
        - name: sample
          in: query
          required: false
          type: string
        responses:
          '200':
            description: 200 response
            schema:
              $ref: '#/definitions/Sample'
  definitions:
    Sample:
      type: object
```

### api_id
The id of your REST API.  
This is written on automatically when you deployed your API with the `-w` option.

### stage
The name of the stage in API Gateway.

### cors
CORS (Cross-Origin Resource Sharing) options.  
If you did not set the `x-amazon-apigateway-integration` option, these are set automatically.

- origin  
For the response's header that named "Access-Control-Allow-Origin".
- headers  
For the response's header that named "Access-Control-Allow-Headers".
- methods  
For the response's header that named "Access-Control-Allow-Methods".

### configuration
The settings of your APIs written in the `Swagger` format.  
If you did not set the `x-amazon-apigateway-integration` option, these are set automatically.

# Commands

### build

- Build and archive your code and libraries to `<your-function-name>.zip`
- Store the secret informations to the archive

```sh
lamvery build [-e <env-name>=<env-value>]
```

### deploy

- Build and deploy your code and libraries
- Store the secret informations to the archive
- Update configuration of the function
- Set alias to a version of the function

```sh
lamvery deploy [-e <env-name>=<env-value>] [-a <alias>]
```

### rollback

- Rollback to the previous version of the function  

**You must do one of the following to use this command.**

- Deploy with `publish(-p,--publish)` and `alias(-a, --alias)` options.
- Turn on(true) `versioning` and set a value to `default_alias` in the configuration file.

```
lamvery rollback [-a <alias>]
```

### set-alias

- Set alias to a version of the function

```sh
lamvery set-alias -a <alias> -v <alias-version>
```

### encrypt

- Encrypt a text value using KMS

```sh
lamvery encrypt [-s] -n <secret-name> <secret-value>
```

### decrypt

- Decrypt the secret information using KMS

```sh
lamvery decrypt -n <secret-name>
```

### events

- Apply CloudWatch Events settings

```sh
lamvery events [-k] [-a <alias>]
```

### invoke

- Invoke the function and output result

```sh
lamvery invoke [-a <alias>] [-v <version>] '{"foo": "bar"}'
```
or
```sh
lamvery invoke [-a <alias>] [-v <version>] path/to/input.json
```

### logs

- Watch the log events of the function

```sh
lamvery logs [-f] [-F <filter>] [-s <start-time-string>] [-i <interval-seconds>]
```

### api

- Manage your APIs

```sh
lamvery api [-r] [-s <stage-name>] [-w]
```

## Options

### `-a` or `--alias`  
This option is needed by the `deploy`,`set-alias`,`invoke`,`rollback`,`events`,`api` commands.  
Alias for a version of the function.

### `-c` or `--conf-file`  
This option needed by all commands.  
Specify the configuration file.  
default: `.lamvery.yml`

### `-d` or `--dry-run`  
This option is needed by the `deploy`,`alias`,`rollback`,`events`,`api` commands.  
Output the difference of configuration and the alias without updating.

### `-s` or `--single-file`  
This option is needed by the `archive` and `deploy` command.  
Archive only the lambda function file, so you can inline edit in the AWS Management Console.

### `-l` or `--no-libs`  
This option is needed by the `archive` and `deploy` command.  
Archive without all libraries.

### `-n` or `--secret-name`  
This option is needed by the `encrypt` and `decrypt` commands.  
The name of the secret value.

### `-p` or `--publish`  
This option is only needed by the `deploy` command.
Publish the version as an atomic operation.

### `-k` or `--keep-empty-events`  
This option is only needed by the `events` command.
Keep the empty CloudWatch Event Rule that does not have CloudWatch Event Target.

### `-s` or `--store`  
This option is only needed by the `encrypt` command.  
Store encripted value to configuration file (default: `.lamvery.yml`).  
Requires the `-n` or `--secret-name` option.

### `-v` or `--version`  
This option is needed by the `set-alias`,`invoke`,`rollback` commands.  
Version of the function.

### `-f` or `--follow`  
This option is only needed by the `logs` command.  
Watch the log events and updates the display (like `tail -f`).

### `-F` or `--filter`  
This option is only needed by the `logs` command.  
Filtering pattern for the log messages.

### `-i` or `--interval`  
This option is only needed by the `logs` command.  
Intervals(seconds) to watch the log events.

### `-s` or `--start`  
This option is only needed by the `logs` command.  
Time to start the log events watching.  
Examples: `yesterday`,`"-1 h"`, `"2016-01-01"`, `"2016-01-01 10:20:30"`

### `-t` or `--target`  
This option is only needed by the `set-alias` command.  
The alias of the version that is targeted for setting alias.

### `-e` or `--env`
This option is needed by the `archive` and `deploy` commands.  
Environment variables that pass to the function.  
**This option can be used repeatedly to pass multiple variables.**  
Examples: `FOO=BAR`

### `-r` or `--remove`  
This option is only needed by the `api` command.  
Remove your APIs.

### `-s` or `--stage`  
This option is only needed by the `api` command.  
The name of the stage in API Gateway.

## `-w` or `--write-id`
This option is only needed by the `api` command.  
Write the id of your API to the configuration file (default: `.lamvery.api.yml`)

# How to use the confidential informations in the lambda function

### 1. Create key on KMS  
See: https://docs.aws.amazon.com/kms/latest/developerguide/create-keys.html

### 2. Create IAM role for lambda function  
Policy example:  
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "kms:Decrypt"
            ],
            "Resource": [
                "arn:aws:kms:us-east-1:<your-account-number>:key/<your-key-id>"
            ]
        }
    ]
}
```

### 3. Set the key-id to your configuration file  
Configuration example:  

- .lamvery.yml

```yml
profile: default
region: us-east-1
versioning: false
default_alias: null
configuration:
  name: sample_lambda_function
  runtime: python2.7 # or nodejs
  role: arn:aws:iam::000000000000:role/lambda_basic_execution
  handler: lambda_function.lambda_handler
  description: This is sample lambda function.
  timeout: 10
  memory_size: 128
```

- .lamvery.secret.yml

```yml
key_id: xxxx-yyyy-zzzz # <-here!
cipher_texts: {}
```

### 4. Encrypt and store the confidential information to your configuration file  
Command example:  
```sh
lamvery encrypt -s -n foo "This is a secret"
```

### 5. Write your function  
Code example:  

- Python

```py
  import lamvery

  def lambda_handler(event, context):
      print(lamvery.secret.get('foo'))
```

- Node.js

```js
var lamvery = require('./lamvery.js');

exports.lambda_handler = function(event, context) {
    lamvery.secret.get('foo', function(err, data) {
        console.log(data);
    });
}
```

### 6. Deploy your function  
Command example:  
```sh
lamvery deploy
```

### 7. Invoke your function  
Command example:  
```sh
lamvery invoke {}
```

Result example:  
```
START RequestId: 13829c9c-9f13-11e5-921b-6f048cff3c2d Version: $LATEST
This is a secret
END RequestId: 13829c9c-9f13-11e5-921b-6f048cff3c2d
```

# How to use the environment variables in the lambda function

### 1. Write your function

- Python

```py
import lamvery
import os


def lambda_handler(event, context):
    lamvery.env.load()
    print(os.environ['FOO'])
    print(os.environ['BAZ'])
```

- Node.js

```js
var lamvery = require('./lamvery.js');

exports.lambdaHandler = function(event, context) {
    lamvery.env.load();
    console.log(process.env.FOO);
    console.log(process.env.BAZ);
}

```

### 2. Deploy your code with `-e` or `--env` options

```sh
lamvery deploy -e FOO=BAR -e BAZ=QUX
```

### 3. Invoke your function

Command example:  
```sh
lamvery invoke {}
```

Result example:  
```
START RequestId: 481f2f8a-d64c-11e5-9ebe-4347553b89b4 Version: 25
BAR
QUX
END RequestId: 481f2f8a-d64c-11e5-9ebe-4347553b89b4
```

Development
-----------

-   Source hosted at [GitHub](https://github.com/marcy-terui/lamvery)
-   Report issues/questions/feature requests on [GitHub
    Issues](https://github.com/marcy-terui/lamvery/issues)

Pull requests are very welcome! Make sure your patches are well tested.
Ideally create a topic branch for every separate change you make. For
example:

1.  Fork the repo
2.  Create your feature branch (`git checkout -b my-new-feature`)
3.  Commit your changes (`git commit -am 'Added some feature'`)
4.  Push to the branch (`git push origin my-new-feature`)
5.  Create new Pull Request

Authors
-------

Created and maintained by [Masashi Terui](https://github.com/marcy-terui) (<marcy9114@gmail.com>)

License
-------

MIT License (see [LICENSE](https://github.com/marcy-terui/lamvery/blob/master/LICENSE))
