import doctest
import pkgutil
import importlib

import preserves

def load_tests(loader, tests, ignore):
    mods = []
    mods.append(preserves)
    for mi in pkgutil.iter_modules(preserves.__path__, preserves.__name__ + '.'):
        mod = importlib.import_module(mi.name)
        mods.append(mod)

    for mod in mods:
        tests.addTests(doctest.DocTestSuite(mod))

    return tests
