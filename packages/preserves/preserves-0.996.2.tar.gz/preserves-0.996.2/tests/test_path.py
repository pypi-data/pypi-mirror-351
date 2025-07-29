from utils import PreservesTestCase

from preserves import *
from preserves.path import parse

class BasicPathTests(PreservesTestCase):
    def test_identity(self):
        self.assertPreservesEqual(parse('').exec(1), (1,))
        self.assertPreservesEqual(parse('').exec([]), ([],))
        self.assertPreservesEqual(parse('').exec(Record(Symbol('hi'), [])), (Record(Symbol('hi'), []),))

    def test_children(self):
        self.assertPreservesEqual(parse('/').exec([1, 2, 3]), (1, 2, 3))
        self.assertPreservesEqual(parse('/').exec([1, [2], 3]), (1, [2], 3))
        self.assertPreservesEqual(parse('/').exec(Record(Symbol('hi'), [1, [2], 3])), (1, [2], 3))

    def test_label(self):
        self.assertPreservesEqual(parse('.^').exec([1, 2, 3]), ())
        self.assertPreservesEqual(parse('.^').exec([1, [2], 3]), ())
        self.assertPreservesEqual(parse('.^').exec(Record(Symbol('hi'), [1, [2], 3])), (Symbol('hi'),))

    def test_count(self):
        self.assertPreservesEqual(parse('<count / ^ hi>').exec([ Record(Symbol('hi'), [1]),
                                                                 Record(Symbol('no'), [2]),
                                                                 Record(Symbol('hi'), [3]) ]),
                         (2,))
        self.assertPreservesEqual(parse('/ <count ^ hi>').exec([ Record(Symbol('hi'), [1]),
                                                                 Record(Symbol('no'), [2]),
                                                                 Record(Symbol('hi'), [3]) ]),
                         (1, 0, 1))
