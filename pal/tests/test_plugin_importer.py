import sys
import types
import unittest
import importlib
from unittest.mock import patch, Mock

from pal import PluginImporter


class BaseSuite(unittest.TestCase):
    def setUp(self):
        sys.modules['dummy_package'] = types.ModuleType('dummy_package')
        sys.meta_path += [PluginImporter('dummy_package')]

        sys.modules['nested.namespace.test'] = types.ModuleType('nested.namespace.test')
        sys.meta_path += [PluginImporter('nested.namespace.test')]

    def test_exception_if_library_does_not_exists(self):
        with self.assertRaises(ValueError):
            PluginImporter('nonexistant_package')

    def test_basic_import(self):
        plugins = importlib.import_module("dummy_package.plugins")
        self.assertEqual('dummy_package.plugins', plugins.__name__)

    def test_nested_namespace_import(self):
        plugins = importlib.import_module("nested.namespace.test.plugins")
        self.assertEqual('nested.namespace.test.plugins', plugins.__name__)

    @patch('pal.pkg_resources')
    def test_include_foreign_entry_point(self, mck):
        the_plugin_module = types.ModuleType("theplugin")
        ep = Mock()
        ep.name = 'foo'
        ep.module_name = 'bar'
        ep.load.return_value = the_plugin_module
        mck.iter_entry_points.return_value = [(ep)]
        sys.meta_path = [PluginImporter('dummy_package')]
        pl = importlib.import_module("dummy_package.plugins.foo")
        self.assertEqual(the_plugin_module, pl)
