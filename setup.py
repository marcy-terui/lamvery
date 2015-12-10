#!/usr/bin/env python
import sys

from setuptools import setup, find_packages

import lamvery

setup_options = dict(
    name='lamvery',
    version=lamvery.__version__,
    description='Yet another deploy tool for AWS Lambda in the virtualenv environment.',
    long_description='''
See: `GitHub <https://github.com/marcy-terui/lamvery/blob/master/README.md>`__
    ''',
    author='Masashi Terui',
    author_email='marcy9114+pypi@gmail.com',
    url='https://github.com/marcy-terui/lamvery',
    packages=find_packages(exclude=['tests*']),
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points={
    'console_scripts':
        'lamvery = lamvery.cli:main'
    },
    license="MIT License",
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
    keywords='aws lambda',
)

setup(**setup_options)
