"""Unit tests for contextlib.py, and other context managers."""


import sys
import os
import decimal
import tempfile
import unittest
import threading
from contextlib import *  # Tests __all__
from test import support

class ContextManagerTestCase(unittest.TestCase):

    def test_contextmanager_plain(self):
        state = []
        @contextmanager
        def woohoo():
            state.append(1)
            yield 42
            state.append(999)
        with woohoo() as x:
            self.assertEqual(state, [1])
            self.assertEqual(x, 42)
            state.append(x)
        self.assertEqual(state, [1, 42, 999])

    def test_contextmanager_finally(self):
        state = []
        @contextmanager
        def woohoo():
            state.append(1)
            try:
                yield 42
            finally:
                state.append(999)
        try:
            with woohoo() as x:
                self.assertEqual(state, [1])
                self.assertEqual(x, 42)
                state.append(x)
                raise ZeroDivisionError()
        except ZeroDivisionError:
            pass
        else:
            self.fail("Expected ZeroDivisionError")
        self.assertEqual(state, [1, 42, 999])

    def test_contextmanager_no_reraise(self):
        @contextmanager
        def whee():
            yield
        ctx = whee()
        ctx.__enter__()
        # Calling __exit__ should not result in an exception
        self.failIf(ctx.__exit__(TypeError, TypeError("foo"), None))

    def test_contextmanager_trap_yield_after_throw(self):
        @contextmanager
        def whoo():
            try:
                yield
            except:
                yield
        ctx = whoo()
        ctx.__enter__()
        self.assertRaises(
            RuntimeError, ctx.__exit__, TypeError, TypeError("foo"), None
        )

    def test_contextmanager_except(self):
        state = []
        @contextmanager
        def woohoo():
            state.append(1)
            try:
                yield 42
            except ZeroDivisionError as e:
                state.append(e.args[0])
                self.assertEqual(state, [1, 42, 999])
        with woohoo() as x:
            self.assertEqual(state, [1])
            self.assertEqual(x, 42)
            state.append(x)
            raise ZeroDivisionError(999)
        self.assertEqual(state, [1, 42, 999])

    def test_contextmanager_attribs(self):
        def attribs(**kw):
            def decorate(func):
                for k,v in kw.items():
                    setattr(func,k,v)
                return func
            return decorate
        @contextmanager
        @attribs(foo='bar')
        def baz(spam):
            """Whee!"""
        self.assertEqual(baz.__name__,'baz')
        self.assertEqual(baz.foo, 'bar')
        self.assertEqual(baz.__doc__, "Whee!")

class ClosingTestCase(unittest.TestCase):

    # XXX This needs more work

    def test_closing(self):
        state = []
        class C:
            def close(self):
                state.append(1)
        x = C()
        self.assertEqual(state, [])
        with closing(x) as y:
            self.assertEqual(x, y)
        self.assertEqual(state, [1])

    def test_closing_error(self):
        state = []
        class C:
            def close(self):
                state.append(1)
        x = C()
        self.assertEqual(state, [])
        try:
            with closing(x) as y:
                self.assertEqual(x, y)
                1/0
        except ZeroDivisionError:
            self.assertEqual(state, [1])
        else:
            self.fail("Didn't raise ZeroDivisionError")

class FileContextTestCase(unittest.TestCase):

    def testWithOpen(self):
        tfn = tempfile.mktemp()
        try:
            f = None
            with open(tfn, "w") as f:
                self.failIf(f.closed)
                f.write("Booh\n")
            self.failUnless(f.closed)
            f = None
            try:
                with open(tfn, "r") as f:
                    self.failIf(f.closed)
                    self.assertEqual(f.read(), "Booh\n")
                    1/0
            except ZeroDivisionError:
                self.failUnless(f.closed)
            else:
                self.fail("Didn't raise ZeroDivisionError")
        finally:
            try:
                os.remove(tfn)
            except os.error:
                pass

class LockContextTestCase(unittest.TestCase):

    def boilerPlate(self, lock, locked):
        self.failIf(locked())
        with lock:
            self.failUnless(locked())
        self.failIf(locked())
        try:
            with lock:
                self.failUnless(locked())
                1/0
        except ZeroDivisionError:
            self.failIf(locked())
        else:
            self.fail("Didn't raise ZeroDivisionError")

    def testWithLock(self):
        lock = threading.Lock()
        self.boilerPlate(lock, lock.locked)

    def testWithRLock(self):
        lock = threading.RLock()
        self.boilerPlate(lock, lock._is_owned)

    def testWithCondition(self):
        lock = threading.Condition()
        def locked():
            return lock._is_owned()
        self.boilerPlate(lock, locked)

    def testWithSemaphore(self):
        lock = threading.Semaphore()
        def locked():
            if lock.acquire(False):
                lock.release()
                return False
            else:
                return True
        self.boilerPlate(lock, locked)

    def testWithBoundedSemaphore(self):
        lock = threading.BoundedSemaphore()
        def locked():
            if lock.acquire(False):
                lock.release()
                return False
            else:
                return True
        self.boilerPlate(lock, locked)

# This is needed to make the test actually run under regrtest.py!
def test_main():
    support.run_unittest(__name__)

if __name__ == "__main__":
    test_main()
