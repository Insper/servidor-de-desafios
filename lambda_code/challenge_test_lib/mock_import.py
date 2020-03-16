'''
Source: https://blog.ffledgling.com/python-imports-i.html
'''

from importlib.machinery import ModuleSpec
import types
import sys
import builtins


class CustomImport:
    def __init__(self, builtin_import):
        self.custom_modules = {}
        self.builtin_import = builtin_import

    def __call__(self, name, globals=None, locals=None, fromlist=(), level=0):
        if name in self.custom_modules:
            return self.custom_modules[name]
        return self.builtin_import(name, globals, locals, fromlist, level)

    def add_module(self, module_name, module_data):
        module = types.ModuleType(module_name, 'Custom {}'.format(module_name))
        module.__file__ = '<custom {}>'.format(module_name)
        module.__name__ = module_name
        module.__loader__ = None
        for n, v in module_data.items():
            setattr(module, n, v)
        self.custom_modules[module_name] = module
        return module


def register_module(module_name, module_data):
    if not isinstance(builtins.__import__, CustomImport):
        builtin_import = builtins.__import__
        builtins.__import__ = CustomImport(builtin_import)
    return builtins.__import__.add_module(module_name, module_data)


def deactivate_custom_imports():
    if isinstance(builtins.__import__, CustomImport):
        builtins.__import__ = builtins.__import__.builtin_import


# class MockImportFinderAndLoader:
#     def __init__(self, module_name, module_data):
#         self.module_name = module_name
#         self.module_data = module_data
#         self._module = None

#     def find_module(self, fullname, path=None):
#         if self.module_name in fullname:
#             return self
#         return None

#     def load_module(self, fullname):
#         # The importer protocol requires the loader create a new module
#         # object, set certain attributes on it, then add it to
#         # `sys.modules` before executing the code inside the module (which
#         # is when the "module" actually gets code inside it)
#         self._module = types.ModuleType(fullname,
#                                         'Custom {}'.format(self.module_name))
#         self._module.__file__ = '<custom {}>'.format(self.module_name)
#         self._module.__name__ = self.module_name
#         self._module.__loader__ = self
#         for n, v in self.module_data.items():
#             setattr(self._module, n, v)
#         print('RESGISFASD', fullname, self._module)
#         sys.modules[fullname] = self._module
#         return self._module

#     @property
#     def module(self):
#         print('ASDASDASD', self._module, sys.modules.get(self.module_name))
#         if not self._module:
#             self._module = sys.modules.get(self.module_name)
#         return self._module

#     def register(self):
#         sys.meta_path.insert(0, self)

#     def unregister(self):
#         if self in sys.meta_path:
#             sys.meta_path.remove(self)

# def register_module(module_name, module_data):
#     if sys.modules.get(module_name):
#         del sys.modules[module_name]
#     loader = MockImportFinderAndLoader(module_name, module_data)
#     loader.register()
#     return loader
