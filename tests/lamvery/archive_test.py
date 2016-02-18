# -*- coding: utf-8 -*-

import tempfile
import os
import zipfile
import json

from unittest import TestCase
from nose.tools import ok_, eq_, raises
from mock import Mock
from lamvery.archive import Archive
from zipfile import PyZipFile, ZIP_DEFLATED
from lamvery.config import RUNTIME_NODE_JS

JSON_FILE_NAME = 'test.json'


class ArchiveTestCase(TestCase):

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

    def test_create_zipfile(self):
        archive = Archive('test.zip')
        archive._runtime = RUNTIME_NODE_JS
        ok_(hasattr(archive.create_zipfile(), 'read'))
        with PyZipFile(archive._zippath, 'r', compression=ZIP_DEFLATED) as zipfile:
            ok_('lambda_function.pyc' in zipfile.namelist())
            ok_('.lamvery_secret.json' in zipfile.namelist())

    def test_create_zipfile_with_single_file(self):
        archive = Archive('test.zip', function_filename='lambda_function.py', single_file=True)
        archive.create_zipfile()
        with PyZipFile(archive._zippath, 'r', compression=ZIP_DEFLATED) as zipfile:
            ok_('lambda_function.py' in zipfile.namelist())
            ok_(not ('.lamvery_secret.json' in zipfile.namelist()))

    def test_generate_json(self):
        archive = Archive('test.zip')
        archive._generate_json(
            JSON_FILE_NAME, {'foo': 2, 'bar': 3})
        data = json.load(open(JSON_FILE_NAME, 'r'))
        eq_(data.get('foo'), 2)

    def test_archive_dir(self):
        archive = Archive('test.zip')
        archive._archive_dir(self.zipfile, self.pj_root)
        ok_(isinstance(self.zipfile.getinfo('setup.pyc'), zipfile.ZipInfo))

    def test_archive_file(self):
        archive = Archive('test.zip')
        archive._archive_file(
            self.zipfile, os.path.join(self.pj_root, 'setup.py'))
        ok_(isinstance(self.zipfile.getinfo('setup.pyc'), zipfile.ZipInfo))
        archive._archive_file(
            self.zipfile, os.path.join(self.pj_root, 'README.md'))
        ok_(isinstance(self.zipfile.getinfo('README.md'), zipfile.ZipInfo))

    def test_archive_dist(self):
        archive = Archive('test.zip')
        archive._archive_dist(self.zipfile, 'lamvery.js')
        ok_(isinstance(self.zipfile.getinfo('lamvery.js'), zipfile.ZipInfo))

    @raises(KeyError)
    def test_archive_single_file_key_error(self):
        self._single_file = True
        archive = Archive('test.zip', single_file=True)
        archive._archive_file(
            self.zipfile, os.path.join(self.pj_root, 'setup.py'))
        ok_(isinstance(self.zipfile.getinfo('setup.pyc'), zipfile.ZipInfo))

    def test_archive_single_file(self):
        self._single_file = True
        archive = Archive('test.zip', single_file=True)
        archive._archive_file(
            self.zipfile, os.path.join(self.pj_root, 'setup.py'))
        ok_(isinstance(self.zipfile.getinfo('setup.py'), zipfile.ZipInfo))

    def test_is_exclude(self):
        archive = Archive('test.zip', exclude=['^\.lamvery\.yml$'])
        eq_(archive.is_exclude('foo.txt'), False)
        eq_(archive.is_exclude('.lamvery.yml'), True)

    def test_is_exclude_file(self):
        archive = Archive('test.zip')
        eq_(archive.is_exclude_file('test.zip'), True)
        eq_(archive.is_exclude_file('foo.txt'), False)
        archive.is_exclude = Mock(return_value=True)
        eq_(archive.is_exclude_file('foo.txt'), True)

    def test_is_exclude_dir(self):
        archive = Archive('test.zip')
        eq_(archive.is_exclude_dir('.git'), True)
        eq_(archive.is_exclude_dir('foo'), False)
        archive.is_exclude = Mock(return_value=True)
        eq_(archive.is_exclude_file('foo'), True)

    def test_is_source_file(self):
        archive = Archive('test.zip')
        eq_(archive.is_source_file('foo.py'), True)
        eq_(archive.is_source_file('foo.pyc'), True)
        eq_(archive.is_source_file('foo.php'), False)

    def test_get_paths(self):
        archive = Archive('test.zip')
        paths = archive._get_paths()
        ok_(os.path.join(self.pj_root, 'lamvery') in paths)

        archive = Archive('test.zip', no_libs=True)
        paths = archive._get_paths()
        ok_(os.path.join(self.pj_root, 'lamvery') in paths)
        ok_(os.path.join(self.pj_root, 'lambda_function.py') in paths)
        ok_(os.path.join(self.pj_root, 'lambda_function.pyc') in paths)
        ok_(os.path.join(self.pj_root, '.lamvery.yml') in paths)

        archive = Archive('test.zip', function_filename='test.py', single_file=True)
        paths = archive._get_paths()
        ok_(os.path.join(self.pj_root, 'test.py') in paths)
        ok_(not os.path.join(self.pj_root, 'lambda_function.pyc') in paths)
        ok_(not os.path.join(self.pj_root, '.lamvery.yml') in paths)

        del os.environ['VIRTUAL_ENV']
        archive = Archive('test.zip')
        paths = archive._get_paths()
        ok_(os.path.join(self.pj_root, 'lamvery') in paths)

    def test_get_size(self):
        archive = Archive('test.zip')
        archive.create_zipfile()
        ok_(isinstance(archive.get_size(), int))
