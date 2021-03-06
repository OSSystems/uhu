# Copyright (C) 2017 O.S. Systems Software LTDA.
# SPDX-License-Identifier: GPL-2.0

import hashlib
import os

from pkgschema import validate_schema

from uhu.core.object import Object, Modes

from utils import EnvironmentFixtureMixin, FileFixtureMixin


class ModeTestCaseMixin(EnvironmentFixtureMixin, FileFixtureMixin):
    mode = None  # Must be the mode name

    def setUp(self):
        super().setUp()
        cwd = os.getcwd()
        os.chdir('tests/core/fixtures/modes')
        self.addCleanup(os.chdir, cwd)

        self.fn = __file__
        self.size = os.path.getsize(self.fn)
        with open(self.fn, 'br') as fp:
            self.sha256sum = hashlib.sha256(fp.read()).hexdigest()

        self.mode_class = Modes.get(self.mode)
        self.mode_schema = '{}-object.json'.format(self.mode)
        self.default_string_file = '{}_default.txt'.format(self.mode)
        self.full_string_file = '{}_full.txt'.format(self.mode)

        self.default_options = None
        self.default_template = None
        self.default_metadata = None
        self.full_options = None
        self.full_template = None
        self.full_metadata = None

    def get_fixture(self, fn):
        with open(fn) as fp:
            fixture = fp.read().strip()
        return fixture.replace(fn, self.fn)

    def test_can_create_default_object(self):
        obj = Object(self.default_options)
        self.assertEqual(obj.mode, self.mode)
        install_condition_options = [
            'install-condition-pattern-type',
            'install-condition-pattern',
            'install-condition-seek',
            'install-condition-buffer-size'
        ]
        for option in self.mode_class.options:
            if option.metadata in install_condition_options:
                # due to its complexity, install condition will have
                # it own test suite.
                continue
            self.assertEqual(
                obj[option.metadata],
                self.default_options.get(option.metadata, option.default))

    def test_can_create_full_object(self):
        obj = Object(self.full_options)
        self.assertEqual(obj.mode, self.mode)
        for option in self.mode_class.options:
            if not option.volatile:
                self.assertEqual(
                    obj[option.metadata], self.full_options[option.metadata])

    def test_default_template(self):
        obj = Object(self.default_options)
        self.assertEqual(self.default_template, obj.to_template())

    def test_full_template(self):
        obj = Object(self.full_options)
        self.assertEqual(self.full_template, obj.to_template())

    def test_default_metadata(self):
        obj = Object(self.default_options)
        metadata = obj.to_metadata()
        self.assertEqual(self.default_metadata, metadata)
        self.assertIsNone(validate_schema(self.mode_schema, metadata))

    def test_full_metadata(self):
        obj = Object(self.full_options)
        metadata = obj.to_metadata()
        self.assertEqual(self.full_metadata, metadata)
        self.assertIsNone(validate_schema(self.mode_schema, metadata))

    def test_default_string_representation(self):
        obj = Object(self.default_options)
        self.assertEqual(str(obj), self.get_fixture(self.default_string_file))

    def test_full_string_representation(self):
        obj = Object(self.full_options)
        self.assertEqual(str(obj), self.get_fixture(self.full_string_file))

    def test_template_keeps_equal_after_object_load(self):
        obj = Object(self.default_options)
        expected = obj.to_template()
        obj.load()
        observed = obj.to_template()
        self.assertEqual(expected, observed)
