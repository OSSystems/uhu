# Copyright (C) 2016 O.S. Systems Software LTDA.
# This software is released under the MIT License

import os
import unittest

import click

from efu.package import exceptions, File, Package

from ..base import EFUTestCase


class PackageTestCase(EFUTestCase):

    def test_raises_invalid_package_file_with_inexistent_file(self):
        os.environ['EFU_PACKAGE_FILE'] = 'inexistent_package_file.json'
        with self.assertRaises(exceptions.InvalidPackageFileError):
            Package()

    def test_raises_invalid_package_file_when_file_is_not_json(self):
        os.environ['EFU_PACKAGE_FILE'] = __file__
        with self.assertRaises(exceptions.InvalidPackageFileError):
            Package()

    def test_can_load_package_file(self):
        files = [self.create_file(b'0') for _ in range(15)]
        id_ = 1234
        version = '2.0'
        os.environ['EFU_PACKAGE_FILE'] = self.create_package_file(
            product_id=id_, version=version, files=files)
        package = Package()

        self.assertEqual(package.product_id, id_)
        self.assertEqual(package.version, version)
        self.assertEqual(len(package.files), len(files))
        for file in package.files.values():
            self.assertIsInstance(file, File)

    def test_package_as_dict(self):
        files = [self.create_file(bytes(i)) for i in range(3)]
        os.environ['EFU_PACKAGE_FILE'] = self.create_package_file(
            product_id=123, version='2.0', files=files)
        observed = Package().as_dict()
        self.assertEqual(observed['version'], '2.0')
        self.assertEqual(len(observed['objects']), len(files))
        for file in observed['objects']:
            self.assertIsNotNone(file['id'])
            self.assertIsNotNone(file['sha256sum'])

    def test_package_metadata(self):
        files = [self.create_file(bytes(i)) for i in range(3)]
        os.environ['EFU_PACKAGE_FILE'] = self.create_package_file(
            product_id='10', version='2.0', files=files)
        observed = Package().metadata

        self.assertEqual(observed['product'], '10')
        self.assertEqual(observed['version'], '2.0')
        self.assertEqual(len(observed['images']), len(files))

        for file in observed['images']:
            self.assertIsNotNone(file['sha256sum'])
            self.assertIsNotNone(file['filename'])
            self.assertIsNotNone(file['size'])
