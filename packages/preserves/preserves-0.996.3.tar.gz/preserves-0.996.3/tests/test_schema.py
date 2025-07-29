from utils import PreservesTestCase

from preserves import *
from preserves.schema import meta, Compiler

def literal_schema(modname, s):
    c = Compiler()
    c.load_schema((Symbol(modname),), preserve(s))
    return c.root

class BasicSchemaTests(PreservesTestCase):
    def test_dictionary_literal(self):
        m = literal_schema(
            's',
            parse('''
<schema {
  version: 1,
  embeddedType: #f,
  definitions: {
    C: <dict {"core": <lit true>}>
  }
}>
'''))
        self.assertEqual(m.s.C.decode({'core': Symbol('true')}), m.s.C())
        self.assertPreservesEqual(preserve(m.s.C()), {'core': Symbol('true')})

    def test_alternation_of_dictionary_literal(self):
        m = literal_schema(
            's',
            parse('''
<schema {
  version: 1,
  embeddedType: #f,
  definitions: {
    C: <or [
      ["notcore" <dict {"notcore": <lit true>}>]
      ["core" <dict {"core": <lit true>}>]
    ]>
  }
}>
'''))
        self.assertEqual(m.s.C.decode({'core': Symbol('true')}), m.s.C.core())
        self.assertPreservesEqual(preserve(m.s.C.core()), {'core': Symbol('true')})
        self.assertEqual(m.s.C.decode({'notcore': Symbol('true')}), m.s.C.notcore())
        self.assertPreservesEqual(preserve(m.s.C.notcore()), {'notcore': Symbol('true')})
