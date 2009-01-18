"""Test case-sensitivity (PEP 235)."""
import importlib
from .. import support
import os
import sys
from test import support as test_support
import unittest


@support.case_insensitive_tests
class CaseSensitivityTest(unittest.TestCase):

    """PEP 235 dictates that on case-preserving, case-insensitive file systems
    that imports are case-sensitive unless the PYTHONCASEOK environment
    variable is set."""

    name = 'MoDuLe'
    assert name != name.lower()

    def find(self, path):
        finder = importlib.PyFileImporter(path)
        return finder.find_module(self.name)

    def sensitivity_test(self):
        """Look for a module with matching and non-matching sensitivity."""
        sensitive_pkg = 'sensitive.{0}'.format(self.name)
        insensitive_pkg = 'insensitive.{0}'.format(self.name.lower())
        with support.create_modules(insensitive_pkg, sensitive_pkg) as mapping:
            sensitive_path = os.path.join(mapping['.root'], 'sensitive')
            insensitive_path = os.path.join(mapping['.root'], 'insensitive')
            return self.find(sensitive_path), self.find(insensitive_path)

    def test_sensitive(self):
        with test_support.EnvironmentVarGuard() as env:
            env.unset('PYTHONCASEOK')
            sensitive, insensitive = self.sensitivity_test()
            self.assert_(hasattr(sensitive, 'load_module'))
            self.assert_(self.name in sensitive._base_path)
            self.assert_(insensitive is None)

    def test_insensitive(self):
        with test_support.EnvironmentVarGuard() as env:
            env.set('PYTHONCASEOK', '1')
            sensitive, insensitive = self.sensitivity_test()
            self.assert_(hasattr(sensitive, 'load_module'))
            self.assert_(self.name in sensitive._base_path)
            self.assert_(hasattr(insensitive, 'load_module'))
            self.assert_(self.name in insensitive._base_path)


def test_main():
    test_support.run_unittest(CaseSensitivityTest)


if __name__ == '__main__':
    test_main()
