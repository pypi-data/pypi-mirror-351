from utils import PreservesTestCase

from preserves import *
from preserves.compare import *

class BasicCompareTests(PreservesTestCase):
    def test_eq_identity(self):
        self.assertTrue(eq(1, 1))
        self.assertFalse(eq(1, 1.0))
        self.assertTrue(eq([], []))
        self.assertTrue(eq(Record(Symbol('hi'), []), Record(Symbol('hi'), [])))

    def test_cmp_identity(self):
        self.assertEqual(cmp(1, 1), 0)
        self.assertEqual(cmp(1, 1.0), 1)
        self.assertEqual(cmp(1.0, 1), -1)
        self.assertEqual(cmp([], []), 0)
        self.assertEqual(cmp([], {}), -1)
        self.assertEqual(cmp(Record(Symbol('hi'), []), Record(Symbol('hi'), [])), 0)
