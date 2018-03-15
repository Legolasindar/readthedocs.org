# -*- coding: utf-8 -*-
from __future__ import (
    absolute_import, division, print_function, unicode_literals)

from collections import namedtuple
import tempfile

from django.test import TestCase
from mock import patch
import pytest

from readthedocs.doc_builder.backends.sphinx import BaseSphinx
from readthedocs.projects.exceptions import ProjectConfigurationError
from readthedocs.projects.models import Project


class SphinxBuilderTest(TestCase):

    fixtures = ['test_data']

    def setUp(self):
        self.project = Project.objects.get(slug='pip')
        self.version = self.project.versions.first()

        build_env = namedtuple('project', 'version')
        build_env.project = self.project
        build_env.version = self.version

        BaseSphinx.type = 'base'
        BaseSphinx.sphinx_build_dir = tempfile.mkdtemp()
        self.base_sphinx = BaseSphinx(build_env=build_env, python_env=None)

    @patch('readthedocs.doc_builder.backends.sphinx.BaseSphinx.create_index')
    @patch('readthedocs.doc_builder.backends.sphinx.BaseSphinx.get_config_params')
    @patch('readthedocs.doc_builder.backends.sphinx.BaseSphinx.run')
    @patch('readthedocs.builds.models.Version.get_conf_py_path')
    def test_create_conf_py(self, get_conf_py_path, run, get_config_params, create_index):
        """
        Test for a project without ``conf.py`` file.

        When this happen, the ``get_conf_py_path`` raises a
        ``ProjectConfigurationError`` which is captured by our own code and
        generates a conf.py file based using our own template.

        This template should be properly rendered in Python2 and Python3 without
        any kind of exception raised by ``append_conf`` (we were originally
        having a ``TypeError`` because of an encoding problem in Python3)
        """
        create_index.return_value = 'README.rst'
        get_config_params.return_value = {}
        get_conf_py_path.side_effect = ProjectConfigurationError
        try:
            self.base_sphinx.append_conf()
        except Exception:
            pytest.fail('Exception was generated when append_conf called.')
