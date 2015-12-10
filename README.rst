=======
Lamvery
=======

.. image:: https://img.shields.io/travis/marcy-terui/lamvery/master.svg
    :target: https://travis-ci.org/marcy-terui/lamvery

.. image:: https://img.shields.io/coveralls/marcy-terui/lamvery.svg
    :target: https://coveralls.io/github/marcy-terui/lamvery

.. image:: https://img.shields.io/pypi/v/lamvery.svg
    :target: https://pypi.python.org/pypi/lamvery

.. image:: https://img.shields.io/pypi/dm/lamvery.svg
    :target: https://pypi.python.org/pypi/lamvery/


Yet another deploy tool for AWS Lambda in the virtualenv.

Requirements
------------

-  Python2.7

-  virtualenv

Installation
------------

.. code::

    virtualenv -p <path-to-python2.7> .venv
    . .venv/bin/activate
    pip install lamvery

Setup
-----

At first,

.. code::

    lamvery init

And put your ``lamvery.yml`` like this.

.. code::
    profile: default
    region: us-east-1
    configuration:
      name: sample_lambda_function
      runtime: python2.7
      role: arn:aws:iam::000000000000:role/lambda_basic_execution
      handler: lambda_function.lambda_handler
      description: This is sample lambda function.
      timeout: 10
      memory_size: 128
    secret:
      key: xxxx-yyyy-zzzz
      cipher_texts:
        foo: !!binary |
          fsdiugfhaeiotgheat+d9yJMyY1uw1i7tYVvQz9I8+e2UBKTAQEBAgB4uMVvZYOx2sWrnnjfnfci
          TMmNbsNYu7WFb0M/fsampogdgoiejeijgdpijgdogjegjoepgjspogfkspofksaopfkaseopfkso
          fsdifsaiogjsaigjsaiogjsaiogjasoigjsaigjasgiasgojsogjsaojsogag+ty6FvbtAFsn3/B
          Kj2+VwQVgD1zO3lTkQ==

Commands
-----

archive
~~~~~~~

- Archive your code and libraries to ``<your-function-name>.zip``
- Store secret informations to the archive

.. code::

    lamvery archive

deploy
~~~~~~

- Archive and deploy your code and libraries
- Store secret informations to the archive
- Update configuration of the function
- Set alias to a version of the function

.. code::

    lamvery deploy

set-alias
~~~~~~~~~

- Set alias to a version of the function

.. code::

    lamvery set-alias -a <alias> -v <alias-version>

encrypt
~~~~~~~~~

- Encrypt a text value using KMS

.. code::

    lamvery encrypt -n <secret-name> <secret-value> [-s]

decrypt
~~~~~~~~~

- Decrypt the secret value using KMS

.. code::

    lamvery decrypt -n <secret-name>

Options
-------

``-a`` or ``--alias``
    | This option needed by ``deploy`` and ``alias`` commands.
    | Alias for a version of the function.
    |

``-c`` or ``--conf-file``
    | This option needed by all commands.
    | Specify the configuration file.
    | default: ``lamvery.yml``
    |

``-d`` or ``--dry-run``
    | This option needed by ``deploy`` and ``alias`` commands.
    | Output the difference of configuration and the alias without updating.
    |

``-n`` or ``--secret-name``
    | This option needed by ``encrypt`` and ``decrypt`` commands.
    | The name of the secret value.
    |

``-p`` or ``--publish``
    | This option only needed by ``deploy`` command.
    | Publish the version as an atomic operation.
    |

``-s`` or ``--store``
    | This option only needed by ``encrypt`` command.
    | Store encripted value to configuration file (default: .lamvery.yml).
    | This option is required `-n` or `--secret-name` option.
    |

``-v`` or ``--alias-version``
    | This option only needed by ``alias`` command.
    | Version of the function to set the alias.
    |

Configuration file (lamvery.yml)
--------------------------------

profile
~~~~~~
The name of a profile to use. If not given, this depends on ``boto3``.

region
~~~~~~
| The region name of your environment.
| If you doesn't set this option, this depends on ``boto3``.

configuration
~~~~~~~~~~~~~

name
    | The name of your function.
    |

runtime
    | The runtime environment for the Lambda function you are uploading.
    | Currently, ``lamvery`` supports only ``python2.7``.
    |

role
    | The Amazon Resource Name (ARN) of the IAM role for your function.
    |

handler
    | The function within your code that Lambda calls to begin execution.
    |

description
    | The description of your function.
    |

timeout
    | The function execution time(seconds) at which Lambda should terminate the function.
    |

memory\_size
    | The amount of memory for your function environment.
    |

alias
    | The default alias when not given ``-a`` or ``--alias`` argument.
    |

secret
~~~~~~~~~~~~~

key
    | The ID of your encryption key on KMS
    |

cipher\_texts
    | The name and cipher texts for passing to lambda function.
    |

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

MIT License (see
`LICENSE <https://github.com/marcy-terui/lamvery/blob/master/LICENSE>`__)
