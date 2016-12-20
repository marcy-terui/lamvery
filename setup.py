#!/usr/bin/env python
import os

from setuptools import setup, find_packages

description = 'User-friendly deploy and management tool for AWS Lambda function.'
long_description = description
if os.path.exists('README.txt'):
    long_description = open('README.txt').read()

setup_options = dict(
    name='lamvery',
    version='0.18.0',
    description=description,
    long_description=long_description,
    author='Masashi Terui',
    author_email='marcy9114+pypi@gmail.com',
    url='https://github.com/marcy-terui/lamvery',
    packages=find_packages(exclude=['tests*', 'lambda_function', 'register']),
    package_data={
        'lamvery': ['dists/lamvery.js']
    },
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points={
        'console_scripts': 'lamvery = lamvery.cli:main'
    },
    license="MIT License",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='aws lambda',
)

setup(**setup_options)
