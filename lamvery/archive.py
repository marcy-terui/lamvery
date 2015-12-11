# -*- coding: utf-8 -*-

import os
import sys
import tempfile
import shutil
import re
import yaml
import lamvery.secret
from zipfile import PyZipFile, ZIP_DEFLATED

EXCLUDE_FILE = [
    'python',
    'python27',
    'python2.7',
    'lamvery',
    'pip',
    'pbr',
    'wheel'
]

EXCLUDE_DIR = [
    '.git',
    '__pycache__'
]

PYFILE_PATTERN = re.compile('.+\.py.?$')

class Archive:

    def __init__(self, filename, secret={}):
        self._filename = filename
        self._tmpdir = tempfile.mkdtemp(suffix='lamvery')
        self._zippath = os.path.join(self._tmpdir, self._filename)
        self._secretpath = os.path.join(self._tmpdir, lamvery.secret.SECRET_FILE_NAME)
        self._secret = secret

    def __del__(self):
        shutil.rmtree(self._tmpdir)

    def create_zipfile(self):
        lamvery.secret.generate(self._secretpath, self._secret)
        with PyZipFile(self._zippath, 'w', compression=ZIP_DEFLATED) as zipfile:
            for p in self._get_paths():
                if os.path.isdir(p):
                    self._archive_dir(zipfile, p)
                else:
                    self._archive_file(zipfile, p)
            self._archive_file(zipfile, self._secretpath)
        return open(self._zippath, 'rb')

    def _archive_dir(self, zipfile, path):
        dirname = os.path.basename(path)
        if not self.is_exclude_dir(dirname):
            zipfile.writepy(path)
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    f_path = os.path.join(dirpath, filename)
                    if not self.is_source_file(filename) and not self.is_exclude_file(filename):
                        f_name = f_path.replace(os.path.dirname(path) + os.sep, '')
                        try:
                            zipfile.getinfo(f_name)
                        except KeyError:
                            zipfile.write(f_path, f_name)

    def _archive_file(self, zipfile, path):
        filename = os.path.basename(path)
        if not self.is_exclude_file(filename):
            if PYFILE_PATTERN.match(filename) is None:
                try:
                    zipfile.getinfo(filename)
                except KeyError:
                    zipfile.write(path, filename)
            elif filename.endswith('.py'):
                try:
                    zipfile.getinfo('{}c'.format(filename))
                except KeyError:
                    zipfile.writepy(path)

    def is_exclude_file(self, name):
        for ex in EXCLUDE_FILE:
            if name == ex:
                return True
        if name == self._filename:
            return True
        return False

    def is_exclude_dir(self, name):
        for ex in EXCLUDE_DIR:
            if name == ex:
                return True
        return False

    def is_source_file(self, name):
        return PYFILE_PATTERN.match(name) is not None

    def _get_paths(self):
        try:
            venv = os.environ['VIRTUAL_ENV']
        except:
            msg = 'VIRTUAL_ENV environment variable can not be found. Are you running in virtualenv?'
            raise Exception(msg)
        paths = []
        for p in sys.path:
            if p.startswith(venv) and os.path.exists(p):
                if os.path.isdir(p):
                    for f in os.listdir(p):
                        f_path = os.path.join(p ,f)
                        paths.append(f_path)
        for f in os.listdir(os.getcwd()):
            f_path = os.path.join(os.getcwd() ,f)
            if not f_path == venv:
                paths.append(f_path)
        return paths
