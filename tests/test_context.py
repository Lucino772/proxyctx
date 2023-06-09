import unittest
from contextvars import ContextVar

from proxyctx import Context

_sentinel = object()


class TestContext(unittest.TestCase):
    def setUp(self) -> None:
        self.local = ContextVar("local")

    def test_push_pop(self):
        context = Context(self.local)
        token = self.local.set(_sentinel)

        context.push()
        self.assertEqual(len(context._cv_tokens), 1)
        self.assertEqual(self.local.get(), context)
        context.pop()
        self.assertEqual(len(context._cv_tokens), 0)
        self.assertEqual(self.local.get(), _sentinel)

        self.local.reset(token)

    def test_push_pop_error(self):
        context = Context(self.local)
        token = self.local.set(_sentinel)

        context.push()
        self.local.set(_sentinel)
        with self.assertRaises(AssertionError):
            context.pop()

        self.local.reset(token)

    def test_context_manager(self):
        context = Context(self.local)
        token = self.local.set(_sentinel)

        with context:
            self.assertEqual(len(context._cv_tokens), 1)
            self.assertEqual(self.local.get(), context)

        self.assertEqual(len(context._cv_tokens), 0)
        self.assertEqual(self.local.get(), _sentinel)

        self.local.reset(token)
