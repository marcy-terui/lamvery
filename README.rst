Lamvery
=======

Yet another deploy tool for AWS Lambda in the virtualenv.

Requirements
------------

-  Python2.7

-  virtualenv

Installation
------------

.. code:: sh

    pip install lamvery

Setup
-----

At first,

.. code:: sh

    lamvery init

And put your ``lamvery.yml`` like this.

.. code:: yml

    name: sample_lambda_function
    runtime: python2.7
    role: arn:aws:iam::000000000000:role/lambda_basic_execution
    handler: lambda_function.lambda_handler
    description: This is sample lambda function.
    timeout: 10
    memory_size: 128
    publish: true

Usage
-----

- Archive your code and libraries to ``<your-function-name>.zip``

.. code:: sh

    lamvery archive

- Archive and deploy your code and libraries

.. code:: sh

    lamvery deploy

Options
-------

- ``-f`` or ``--file``

| Specify the configuration file.
| default: ``lamvery.yml``

Configuration
-------------

name
~~~~

The name of your function.

runtime
~~~~~~~

| The runtime environment for the Lambda function you are uploading.
| Currently, ``lamvery`` supports only ``python2.7``.

name
~~~~

The name of your function.

role
~~~~

The Amazon Resource Name (ARN) of the IAM role for your function.

handler
~~~~~~~

The function within your code that Lambda calls to begin execution.

description
~~~~~~~~~~~

The description of your function.

timeout
~~~~~~~

The function execution time(seconds) at which Lambda should terminate
the function.

memory\_size
~~~~~~~~~~~~

The amount of memory for your function environment.

publish
~~~~~~~

This boolean parameter can be used to request AWS Lambda to
create/update the Lambda function and publish a version as an atomic
operation.

Development
-----------

-  Source hosted at `GitHub <https://github.com/marcy-terui/lamvery>`__
-  Report issues/questions/feature requests on `GitHub
   Issues <https://github.com/marcy-terui/lamvery/issues>`__

Pull requests are very welcome! Make sure your patches are well tested.
Ideally create a topic branch for every separate change you make. For
example:

1. Fork the repo
2. Create your feature branch (``git checkout -b my-new-feature``)
3. Commit your changes (``git commit -am 'Added some feature'``)
4. Push to the branch (``git push origin my-new-feature``)
5. Create new Pull Request

Authors
-------

Created and maintained by `Masashi
Terui <https://github.com/marcy-terui>`__ (marcy9114@gmail.com)

License
-------

Apache 2.0 (see
`LICENSE <https://github.com/marcy-terui/lamvery/blob/master/LICENSE>`__)
