# -*- coding: utf-8 -*-

import os
import sys
import tempfile
import shutil
import re
import warnings
import json
import lamvery.secret
import lamvery.config

from zipfile import PyZipFile, ZIP_DEFLATED
from lamvery.log import get_logger
from lamvery.utils import run_commands

warnings.simplefilter("ignore", UserWarning)

EXCLUDE_DIR = [
    '.git',
    '__pycache__'
]

PYFILE_PATTERN = re.compile('.+\.py.?$')


class Builder:

    def __init__(
        self,
        filename,
        function_filename=None,
        single_file=False,
        no_libs=False,
        secret={},
        exclude=[],
        runtime=lamvery.config.RUNTIME_PY_27,
        env=None,
        clean_build=False,
        hooks={}
    ):
        self._filename = filename
        self._function_filename = function_filename
        self._tmpdir = tempfile.mkdtemp(suffix='lamvery')
        self._zippath = os.path.join(self._tmpdir, self._filename)
        self._secret = secret
        self._single_file = single_file
        self._no_libs = no_libs
        self._exclude = exclude
        self._runtime = runtime
        self._env = env
        self._clean_build = clean_build
        self._clean_build_dir = tempfile.mkdtemp(suffix='lamvery-build')
        self._hooks = hooks

    def __del__(self):
        shutil.rmtree(self._tmpdir)

    def build(self):
        if self._clean_build:
            self._prepare_clean_build()

        self._run_hooks(self._hooks.get('pre', []))

        with PyZipFile(self._zippath, 'w', compression=ZIP_DEFLATED) as zipfile:
            for p in self._get_paths():
                if os.path.isdir(p):
                    self._archive_dir(zipfile, p)
                else:
                    self._archive_file(zipfile, p)

            if not self._single_file:
                secret_path = os.path.join(self._tmpdir, lamvery.secret.SECRET_FILE_NAME)
                env_path = os.path.join(self._tmpdir, lamvery.env.ENV_FILE_NAME)
                self._generate_json(secret_path, self._secret)
                self._generate_json(env_path, self._env)
                self._archive_file(zipfile, secret_path)
                self._archive_file(zipfile, env_path)

                if self._runtime == lamvery.config.RUNTIME_NODE_JS:
                    self._archive_dist(zipfile, 'lamvery.js')

        self._run_hooks(self._hooks.get('post', []))

        return open(self._zippath, 'rb')

    def _prepare_clean_build(self):
        for p in os.listdir(os.getcwd()):
            path = os.path.join(os.getcwd(), p)
            if not path.startswith(os.environ.get('VIRTUAL_ENV')):
                if os.path.isdir(path):
                    shutil.copytree(path, os.path.join(self._clean_build_dir, p))
                else:
                    shutil.copyfile(path, os.path.join(self._clean_build_dir, p))

    def _run_hooks(self, hooks):
        if self._clean_build:
            return run_commands(hooks, self._clean_build_dir)
        else:
            return run_commands(hooks)

    def _generate_json(self, path, data):
        if not isinstance(data, dict):
            data = {}

        json.dump(
            data,
            open(path, 'w'))

    def _archive_dist(self, zipfile, dist):
        self._archive_file(
            zipfile, os.path.join(os.path.dirname(__file__), 'dists', dist))

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
                    zipfile.getinfo('{}o'.format(filename))
                except KeyError:
                    if self._single_file:
                        zipfile.write(path, filename)
                    else:
                        zipfile.writepy(path)

    def is_exclude(self, name):
        for ex in self._exclude:
            if re.compile(ex).match(name) is not None:
                return True
        return False

    def is_exclude_file(self, name):
        if self.is_exclude(name):
            return True
        if name == self._filename:
            return True
        return False

    def is_exclude_dir(self, name):
        if self.is_exclude(name):
            return True
        for ex in EXCLUDE_DIR:
            if name == ex:
                return True
        return False

    def is_source_file(self, name):
        return PYFILE_PATTERN.match(name) is not None

    def _get_paths(self):
        paths = []

        if self._single_file:
            f = self._function_filename
            return [os.path.join(os.getcwd(), f)]

        if self._clean_build:
            for p in os.listdir(self._clean_build_dir):
                paths.append(os.path.join(self._clean_build_dir, p))
            return paths

        logger = get_logger(__name__)
        try:
            venv = os.environ['VIRTUAL_ENV']
        except:
            logger.warn(
                'VIRTUAL_ENV environment variable can not be found. ' +
                'Python libraries are not included in the archive.')
            venv = None

        if not self._no_libs and venv is not None:
            for p in sys.path:
                if os.path.isdir(p) and os.path.exists(p):
                    if p.startswith(venv) and p.find('site-packages') != -1:
                        for f in os.listdir(p):
                            f_path = os.path.join(p, f)
                            paths.append(f_path)
        for f in os.listdir(os.getcwd()):
            f_path = os.path.join(os.getcwd(), f)
            if not f_path == venv:
                paths.append(f_path)

        return paths

    def get_size(self):
        return os.stat(self._zippath).st_size
