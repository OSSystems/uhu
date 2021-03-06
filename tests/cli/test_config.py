# Copyright (C) 2017 O.S. Systems Software LTDA.
# SPDX-License-Identifier: GPL-2.0

import os
import unittest
from configparser import ConfigParser

from click.testing import CliRunner

from uhu.config import Config, AUTH_SECTION
from uhu.utils import LOCAL_CONFIG_VAR
from uhu.cli.config import (
    cleanup_command, get_command, set_command, init_command)
from uhu.utils import GLOBAL_CONFIG_VAR

from utils import FileFixtureMixin, EnvironmentFixtureMixin, UHUTestCase


class ConfigCommandTestCase(
        FileFixtureMixin, EnvironmentFixtureMixin, UHUTestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.config_filename = self.create_file('')
        self.set_env_var(GLOBAL_CONFIG_VAR, self.config_filename)
        self.config = Config()

    def test_can_set_a_configuration(self):
        self.runner.invoke(set_command, args=['foo', 'bar'])
        config = ConfigParser()
        config.read(self.config_filename)
        self.assertEqual(config['settings']['foo'], 'bar')

    def test_can_set_configuration_in_another_section(self):
        section = 'upload'
        self.runner.invoke(
            set_command, args=['foo', 'bar', '--section', section])
        config = ConfigParser()
        config.read(self.config_filename)
        self.assertEqual(config.get(section, 'foo'), 'bar')

    def test_can_get_a_configuration(self):
        with open(self.config_filename, 'w') as fp:
            fp.write('[settings]\n')
            fp.write('foo = bar\n\n')
        result = self.runner.invoke(get_command, args=['foo'])
        self.assertEqual(result.output.strip(), 'bar')

    def test_can_get_configuration_from_another_section(self):
        with open(self.config_filename, 'w') as fp:
            fp.write('[auth]\n')
            fp.write('foo = bar\n\n')
        result = self.runner.invoke(
            get_command, args=['foo', '--section', 'auth'])
        self.assertEqual(result.output.strip(), 'bar')

    def test_can_set_many_values_and_retrieve_them_later(self):
        self.runner.invoke(set_command, args=['foo', 'bar'])
        self.runner.invoke(set_command, args=['bar', 'foo'])
        config = ConfigParser()
        config.read(self.config_filename)
        self.assertEqual(config.get('settings', 'foo'), 'bar')
        self.assertEqual(config.get('settings', 'bar'), 'foo')

    def test_return_none_when_getting_inexistent_configuration(self):
        result = self.runner.invoke(get_command, args=['no-existent'])
        self.assertEqual(result.output, '')

    def test_can_set_init_settings(self):
        lines = '\n'.join(['access', 'secret', __file__])
        result = self.runner.invoke(init_command, input=lines)
        self.assertEqual(result.exit_code, 0)

        access, secret = self.config.get_credentials()
        self.assertEqual(access, 'access')
        self.assertEqual(secret, 'secret')

        path = self.config.get_private_key_path()
        self.assertEqual(path, __file__)


class CleanupCommandTestCase(unittest.TestCase):

    def setUp(self):
        os.environ[LOCAL_CONFIG_VAR] = '.uhu-test'
        self.runner = CliRunner()
        self.addCleanup(os.environ.pop, LOCAL_CONFIG_VAR)

    def test_can_cleanup_uhu_files(self):
        open('.uhu-test', 'w').close()
        self.assertTrue(os.path.exists('.uhu-test'))
        self.runner.invoke(cleanup_command)
        self.assertFalse(os.path.exists('.uhu-test'))

    def test_cleanup_command_returns_0_if_successful(self):
        open('.uhu-test', 'w').close()
        result = self.runner.invoke(cleanup_command)
        self.assertEqual(result.exit_code, 0)

    def test_cleanup_command_returns_1_if_package_is_already_deleted(self):
        result = self.runner.invoke(cleanup_command)
        self.assertEqual(result.exit_code, 1)
