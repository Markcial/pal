import importlib.util
import sys
import traceback
import warnings
import types
import pkg_resources


class PluginImporter(object):
    DEFAULT_EXT_NAME = 'plugins'

    ext_name = None

    def __init__(self, root, ext_name=None):
        self.ext_name = ext_name or self.DEFAULT_EXT_NAME
        self.path = '%s.%s' % (root, self.ext_name)

    def find_module(self, fullname, path=None):
        if fullname.startswith(self.path):
            return self
        return None

    def load_module(self, name):
        print(name)
        if name not in sys.modules:
            spec = importlib.util.spec_from_loader(name, self)
            sys.modules[name] = importlib.util.module_from_spec(spec)
            for entry in pkg_resources.iter_entry_points(name):
                try:
                    sub_module = entry.load()
                except Exception:
                    warnings.warn('Unable to load %s \n\n%s' % (
                        entry, traceback.format_exc()), Warning)
                    continue
                setattr(sys.modules[name], entry.name, sub_module)
                sys.modules['%s.%s' % (name, entry.name)] = sub_module

        return sys.modules[name]


def bap(package, ext_name=None):
    sys.meta_path += [PluginImporter(package, ext_name=ext_name)]