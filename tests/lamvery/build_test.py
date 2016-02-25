# -*- coding: utf-8 -*-

import tempfile
import os
import zipfile
import json

from unittest import TestCase
from nose.tools import ok_, eq_, raises
from mock import Mock
from lamvery.build import Builder
from zipfile import PyZipFile, ZIP_DEFLATED
from lamvery.config import RUNTIME_NODE_JS

JSON_FILE_NAME = 'test.json'


class BuilderTestCase(TestCase):

    def setUp(self):
        tmp = tempfile.mkstemp(prefix=__name__)
        self.zipfile_path = tmp[1]
        self.zipfile = PyZipFile(self.zipfile_path, 'w')
        self.pj_root = os.path.abspath(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    def tearDown(self):
        os.remove(self.zipfile_path)
        try:
            os.remove('test.json')
        except:
            pass

    def test_build(self):
        builder = Builder('test.zip')
        builder._runtime = RUNTIME_NODE_JS
        ok_(hasattr(builder.build(), 'read'))
        with PyZipFile(builder._zippath, 'r', compression=ZIP_DEFLATED) as zipfile:
            ok_('lambda_function.pyc' in zipfile.namelist())
            ok_('.lamvery_secret.json' in zipfile.namelist())

    def test_build_with_single_file(self):
        builder = Builder('test.zip', function_filename='lambda_function.py', single_file=True)
        builder.build()
        with PyZipFile(builder._zippath, 'r', compression=ZIP_DEFLATED) as zipfile:
            ok_('lambda_function.py' in zipfile.namelist())
            ok_(not ('.lamvery_secret.json' in zipfile.namelist()))

    def test_generate_json(self):
        builder = Builder('test.zip')
        builder._generate_json(
            JSON_FILE_NAME, {'foo': 2, 'bar': 3})
        data = json.load(open(JSON_FILE_NAME, 'r'))
        eq_(data.get('foo'), 2)

    def test_archive_dir(self):
        builder = Builder('test.zip')
        builder._archive_dir(self.zipfile, self.pj_root)
        ok_(isinstance(self.zipfile.getinfo('setup.pyc'), zipfile.ZipInfo))

    def test_archive_file(self):
        builder = Builder('test.zip')
        builder._archive_file(
            self.zipfile, os.path.join(self.pj_root, 'setup.py'))
        ok_(isinstance(self.zipfile.getinfo('setup.pyc'), zipfile.ZipInfo))
        builder._archive_file(
            self.zipfile, os.path.join(self.pj_root, 'README.md'))
        ok_(isinstance(self.zipfile.getinfo('README.md'), zipfile.ZipInfo))

    def test_archive_dist(self):
        builder = Builder('test.zip')
        builder._archive_dist(self.zipfile, 'lamvery.js')
        ok_(isinstance(self.zipfile.getinfo('lamvery.js'), zipfile.ZipInfo))

    @raises(KeyError)
    def test_archive_single_file_key_error(self):
        self._single_file = True
        builder = Builder('test.zip', single_file=True)
        builder._archive_file(
            self.zipfile, os.path.join(self.pj_root, 'setup.py'))
        ok_(isinstance(self.zipfile.getinfo('setup.pyc'), zipfile.ZipInfo))

    def test_archive_single_file(self):
        self._single_file = True
        builder = Builder('test.zip', single_file=True)
        builder._archive_file(
            self.zipfile, os.path.join(self.pj_root, 'setup.py'))
        ok_(isinstance(self.zipfile.getinfo('setup.py'), zipfile.ZipInfo))

    def test_is_exclude(self):
        builder = Builder('test.zip', exclude=['^\.lamvery\.yml$'])
        eq_(builder.is_exclude('foo.txt'), False)
        eq_(builder.is_exclude('.lamvery.yml'), True)

    def test_is_exclude_file(self):
        builder = Builder('test.zip')
        eq_(builder.is_exclude_file('test.zip'), True)
        eq_(builder.is_exclude_file('foo.txt'), False)
        builder.is_exclude = Mock(return_value=True)
        eq_(builder.is_exclude_file('foo.txt'), True)

    def test_is_exclude_dir(self):
        builder = Builder('test.zip')
        eq_(builder.is_exclude_dir('.git'), True)
        eq_(builder.is_exclude_dir('foo'), False)
        builder.is_exclude = Mock(return_value=True)
        eq_(builder.is_exclude_file('foo'), True)

    def test_is_source_file(self):
        builder = Builder('test.zip')
        eq_(builder.is_source_file('foo.py'), True)
        eq_(builder.is_source_file('foo.pyc'), True)
        eq_(builder.is_source_file('foo.php'), False)

    def test_get_paths(self):
        builder = Builder('test.zip')
        paths = builder._get_paths()
        ok_(os.path.join(self.pj_root, 'lamvery') in paths)

        builder = Builder('test.zip', no_libs=True)
        paths = builder._get_paths()
        ok_(os.path.join(self.pj_root, 'lamvery') in paths)
        ok_(os.path.join(self.pj_root, 'lambda_function.py') in paths)
        ok_(os.path.join(self.pj_root, 'lambda_function.pyc') in paths)
        ok_(os.path.join(self.pj_root, '.lamvery.yml') in paths)

        builder = Builder('test.zip', function_filename='test.py', single_file=True)
        paths = builder._get_paths()
        ok_(os.path.join(self.pj_root, 'test.py') in paths)
        ok_(not os.path.join(self.pj_root, 'lambda_function.pyc') in paths)
        ok_(not os.path.join(self.pj_root, '.lamvery.yml') in paths)

        builder = Builder('test.zip', clean_build=True)
        paths = builder._get_paths()
        ok_(os.path.join(self.pj_root, 'lamvery') not in paths)

        del os.environ['VIRTUAL_ENV']
        builder = Builder('test.zip')
        paths = builder._get_paths()
        ok_(os.path.join(self.pj_root, 'lamvery') in paths)

    def test_get_size(self):
        builder = Builder('test.zip')
        builder.build()
        ok_(isinstance(builder.get_size(), int))
