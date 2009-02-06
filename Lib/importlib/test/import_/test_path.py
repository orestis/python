from importlib import machinery
from .. import util
from . import util as import_util
from contextlib import nested
import imp
import os
import sys
from test import support
from types import MethodType
import unittest


class BaseTests(unittest.TestCase):

    """When sys.meta_path cannot find the desired module, sys.path is
    consulted. For each entry on the sequence [order], sys.path_importer_cache
    is checked to see if it contains a key for the entry [cache check]. If an
    importer is found then it is consulted before trying the next entry in
    sys.path [cache use]. The 'path' argument to find_module() is never used
    when trying to find a module [path not used].

    If an entry from sys.path is not in sys.path_importer_cache, sys.path_hooks
    is called in turn [hooks order]. If a path hook cannot handle an entry,
    ImportError is raised [hook failure]. Otherwise the resulting object is
    cached in sys.path_importer_cache and then consulted [hook success]. If no
    hook is found, None is set in sys.path_importer_cache and the default
    importer is tried [no hook].

    For use of __path__ in a package, the above is all true, just substitute
    "sys.path" for "__path__".

    """

    def order_test(self, to_import, entry, search_path, path=[]):
        # [order]
        log = []
        class LogFindModule(util.mock_modules):
            def find_module(self, fullname):
                log.append(self)
                return super().find_module(fullname)

        assert len(search_path) == 2
        misser = LogFindModule(search_path[0])
        hitter = LogFindModule(to_import)
        with nested(misser, hitter):
            cache = dict(zip(search_path, (misser, hitter)))
            with util.import_state(path=path, path_importer_cache=cache):
                import_util.import_(to_import)
        self.assertEquals(log[0], misser)
        self.assertEquals(log[1], hitter)

    @import_util.importlib_only  # __import__ uses PyDict_GetItem(), bypassing log.
    def cache_use_test(self, to_import, entry, path=[]):
        # [cache check], [cache use]
        log = []
        class LoggingDict(dict):
            def __getitem__(self, item):
                log.append(item)
                return super(LoggingDict, self).__getitem__(item)

        with util.mock_modules(to_import) as importer:
            cache = LoggingDict()
            cache[entry] = importer
            with util.import_state(path=[entry], path_importer_cache=cache):
                module = import_util.import_(to_import, fromlist=['a'])
            self.assert_(module is importer[to_import])
        self.assertEquals(len(cache), 1)
        self.assertEquals([entry], log)

    def hooks_order_test(self, to_import, entry, path=[]):
        # [hooks order], [hooks failure], [hook success]
        log = []
        def logging_hook(entry):
            log.append(entry)
            raise ImportError
        with util.mock_modules(to_import) as importer:
            hitter = import_util.mock_path_hook(entry, importer=importer)
            path_hooks = [logging_hook, logging_hook, hitter]
            with util.import_state(path_hooks=path_hooks, path=path):
                import_util.import_(to_import)
                self.assertEquals(sys.path_importer_cache[entry], importer)
        self.assertEquals(len(log), 2)

    # [no hook] XXX Worry about after deciding how to handle the default hook.

    def path_argument_test(self, to_import):
        # [path not used]
        class BadImporter:
            """Class to help detect TypeError from calling find_module() with
            an improper number of arguments."""
            def find_module(name):
                raise ImportError

        try:
            import_util.import_(to_import)
        except ImportError:
            pass


class PathTests(BaseTests):

    """Tests for sys.path."""

    def test_order(self):
        self.order_test('hit', 'second', ['first', 'second'],
                        ['first', 'second'])

    def test_cache_use(self):
        entry = "found!"
        self.cache_use_test('hit', entry, [entry])

    def test_hooks_order(self):
        entry = "found!"
        self.hooks_order_test('hit', entry, [entry])

    def test_path_argument(self):
        name = 'total junk'
        with util.uncache(name):
            self.path_argument_test(name)


class __path__Tests(BaseTests):

    """Tests for __path__."""

    def run_test(self, test, entry, path, *args):
        with util.mock_modules('pkg.__init__') as importer:
            importer['pkg'].__path__ = path
            importer.load_module('pkg')
            test('pkg.hit', entry, *args)


    @import_util.importlib_only  # XXX Unknown reason why this fails.
    def test_order(self):
        self.run_test(self.order_test, 'second', ('first', 'second'), ['first',
            'second'])

    def test_cache_use(self):
        location = "I'm here!"
        self.run_test(self.cache_use_test, location, [location])

    def test_hooks_order(self):
        location = "I'm here!"
        self.run_test(self.hooks_order_test, location, [location])

    def test_path_argument(self):
        module = imp.new_module('pkg')
        module.__path__ = ['random __path__']
        name = 'pkg.whatever'
        sys.modules['pkg'] = module
        with util.uncache('pkg', name):
            self.path_argument_test(name)


class FinderTests(unittest.TestCase):

    """Tests for SysPathImporter."""

    def test_failure(self):
        # Test None returned upon not finding a suitable finder.
        def mock_implicit_hooks():
            return []
        # XXX Not blackbox.
        original_hooks = machinery.PathFinder._implicit_hooks
        machinery.PathFinder._implicit_hooks = staticmethod(mock_implicit_hooks)
        try:
            with util.import_state():
                self.assert_(machinery.PathFinder.find_module('XXX') is None)
        finally:
            machinery.PathFinder._implicit_hooks = original_hooks

    def test_sys_path(self):
        # Test that sys.path is used when 'path' is None.
        # Implicitly tests that sys.path_importer_cache is used.
        module = '<test module>'
        path = '<test path>'
        importer = util.mock_modules(module)
        with util.import_state(path_importer_cache={path: importer},
                               path=[path]):
            loader = machinery.PathFinder.find_module(module)
            self.assert_(loader is importer)

    def test_path(self):
        # Test that 'path' is used when set.
        # Implicitly tests that sys.path_importer_cache is used.
        module = '<test module>'
        path = '<test path>'
        importer = util.mock_modules(module)
        with util.import_state(path_importer_cache={path: importer}):
            loader = machinery.PathFinder.find_module(module, [path])
            self.assert_(loader is importer)

    def test_path_importer_cache_has_None(self):
        # Test that the default hook is used when sys.path_importer_cache
        # contains None for a path.
        module = '<test module>'
        importer = util.mock_modules(module)
        path = '<test path>'
        # XXX Not blackbox.
        original_hook = machinery.PathFinder._default_hook
        mock_hook = import_util.mock_path_hook(path, importer=importer)
        machinery.PathFinder._default_hook = staticmethod(mock_hook)
        try:
            with util.import_state(path_importer_cache={path: None}):
                loader = machinery.PathFinder.find_module(module, path=[path])
                self.assert_(loader is importer)
        finally:
            machinery.PathFinder._default_hook = original_hook

    def test_path_hooks(self):
        # Test that sys.path_hooks is used.
        # Test that sys.path_importer_cache is set.
        module = '<test module>'
        path = '<test path>'
        importer = util.mock_modules(module)
        hook = import_util.mock_path_hook(path, importer=importer)
        with util.import_state(path_hooks=[hook]):
            loader = machinery.PathFinder.find_module(module, [path])
            self.assert_(loader is importer)
            self.assert_(path in sys.path_importer_cache)
            self.assert_(sys.path_importer_cache[path] is importer)

    def test_implicit_hooks(self):
        # Test that the implicit path hooks are used.
        existing_path = os.path.dirname(support.TESTFN)
        bad_path = '<path>'
        module = '<module>'
        assert not os.path.exists(bad_path)
        with util.import_state():
            nothing = machinery.PathFinder.find_module(module,
                                                       path=[existing_path])
            self.assert_(nothing is None)
            self.assert_(existing_path in sys.path_importer_cache)
            self.assert_(not isinstance(sys.path_importer_cache[existing_path],
                                        imp.NullImporter))
            nothing = machinery.PathFinder.find_module(module, path=[bad_path])
            self.assert_(nothing is None)
            self.assert_(bad_path in sys.path_importer_cache)
            self.assert_(isinstance(sys.path_importer_cache[bad_path],
                                    imp.NullImporter))


def test_main():
    from test.support import run_unittest
    run_unittest(PathTests, __path__Tests, FinderTests)

if __name__ == '__main__':
    test_main()
