"""The [preserves.schema][] module implements [Preserves
Schema](https://preserves.dev/preserves-schema.html) for Python.

A Schema source file (like [this one](https://preserves.dev/schema/schema.prs)) is first
compiled using [`preserves-schemac`](https://preserves.dev/doc/preserves-schemac.html) to
produce a binary-syntax *schema bundle* containing schema module definitons (like [this
one](https://preserves.dev/preserves-schema.html#appendix-metaschema-instance)). Python code
then loads the bundle, exposing its contents as [Namespace][preserves.schema.Namespace]s
ultimately containing [SchemaObject][preserves.schema.SchemaObject]s.

## Examples

### Setup: Loading a schema bundle

For our running example, we will use schemas associated with the [Syndicated Actor
Model](https://git.syndicate-lang.org/syndicate-lang/syndicate-protocols). (The schema bundle
is a copy of [this
file](https://git.syndicate-lang.org/syndicate-lang/syndicate-protocols/src/branch/main/schema-bundle.bin)
from the `syndicate-protocols` repository.)

To load a schema bundle, use [load_schema_file][preserves.schema.load_schema_file] (or,
alternatively, use [Compiler][preserves.schema.Compiler] directly):

```python
>>> bundle = load_schema_file('docs/syndicate-protocols-schema-bundle.bin')
>>> type(bundle)
<class 'preserves.schema.Namespace'>

```

The top-level entries in the loaded bundle are schema modules. Let's examine the `stream`
schema module, whose [source
code](https://git.syndicate-lang.org/syndicate-lang/syndicate-protocols/src/commit/d8a139b23a40bad6698f9f4240f9e8426b4a123f/schemas/stream.prs)
indicates that it should contain definitions for `Mode`, `Source`, `Sink`, etc.:

```python
>>> bundle.stream                                           # doctest: +ELLIPSIS
{'Mode': <class 'stream.Mode'>, 'Sink': <class 'stream.Sink'>, ...}

```

### Example 1: stream.StreamListenerError, a product type

Drilling down further, let's consider the [definition of
StreamListenerError](https://git.syndicate-lang.org/syndicate-lang/syndicate-protocols/src/commit/d8a139b23a40bad6698f9f4240f9e8426b4a123f/schemas/stream.prs#L9), which appears in the source as

```
StreamListenerError = <stream-listener-error @spec any @message string> .
```

This reads, in the [Preserves Schema
language](https://preserves.dev/preserves-schema.html#the-preserves-schema-language), as the
definition of a simple product type (record, class, object) with two named fields `spec` and
`message`. Parsing a value into a `StreamListenerError` will only succeed if it's a record, if
the label matches, the second field (`message`) is a string, and it has exactly two fields.

```python
>>> bundle.stream.StreamListenerError
<class 'stream.StreamListenerError'>

```

The `StreamListenerError` class includes a [decode][preserves.schema.SchemaObject.decode]
method that analyzes an input value:

```python
>>> bundle.stream.StreamListenerError.decode(
...     parse('<stream-listener-error <xyz> "an error">'))
StreamListenerError {'spec': #xyz(), 'message': 'an error'}

```

If invalid input is supplied, [decode][preserves.schema.SchemaObject.decode] will raise
[SchemaDecodeFailed][preserves.schema.SchemaDecodeFailed], which includes helpful information
for diagnosing the problem (as we will see below, this is especially useful for parsers for sum
types):

```python
>>> bundle.stream.StreamListenerError.decode(
...     parse('<i-am-invalid>'))
Traceback (most recent call last):
  ...
preserves.schema.SchemaDecodeFailed: Could not decode i-am-invalid using <class 'stream.StreamListenerError'>
Most likely reason: in stream.StreamListenerError: <lit stream-listener-error> didn't match i-am-invalid
Full explanation: 
  in stream.StreamListenerError: <lit stream-listener-error> didn't match i-am-invalid

```

Alternatively, the [try_decode][preserves.schema.SchemaObject.try_decode] method catches
[SchemaDecodeFailed][preserves.schema.SchemaDecodeFailed], transforming it into `None`:

```python
>>> bundle.stream.StreamListenerError.try_decode(
...     parse('<stream-listener-error <xyz> "an error">'))
StreamListenerError {'spec': #xyz(), 'message': 'an error'}
>>> bundle.stream.StreamListenerError.try_decode(
...     parse('<i-am-invalid>'))

```

The class can also be instantiated directly:

```python
>>> err = bundle.stream.StreamListenerError(Record(Symbol('xyz'), []), 'an error')
>>> err
StreamListenerError {'spec': #xyz(), 'message': 'an error'}

```

The fields and contents of instances can be queried:

```python
>>> err.spec
#xyz()
>>> err.message
'an error'

```

And finally, instances can of course be serialized and encoded:

```python
>>> print(stringify(err))
<stream-listener-error <xyz> "an error">
>>> canonicalize(err)
b'\\xb4\\xb3\\x15stream-listener-error\\xb4\\xb3\\x03xyz\\x84\\xb1\\x08an error\\x84'

```

### Example 2: stream.Mode, a sum type

Now let's consider the [definition of
Mode](https://git.syndicate-lang.org/syndicate-lang/syndicate-protocols/src/commit/d8a139b23a40bad6698f9f4240f9e8426b4a123f/schemas/stream.prs#L37),
which appears in the source as

```
Mode = =bytes / @lines LineMode / <packet @size int> / <object @description any> .
```

This reads, in the [Preserves Schema
language](https://preserves.dev/preserves-schema.html#the-preserves-schema-language), as an
alternation (disjoint union, variant, sum type) of four possible kinds of value: the symbol
`bytes`; a `LineMode` value; a record with `packet` as its label and an integer as its only
field; or a record with `object` as its label and any kind of value as its only field. In
Python, this becomes:

```python
>>> bundle.stream.Mode.bytes
<class 'stream.Mode.bytes'>
>>> bundle.stream.Mode.lines
<class 'stream.Mode.lines'>
>>> bundle.stream.Mode.packet
<class 'stream.Mode.packet'>
>>> bundle.stream.Mode.object
<class 'stream.Mode.object'>

```

As before, `Mode` includes a [decode][preserves.schema.SchemaObject.decode] method that analyzes
an input value:

```python
>>> bundle.stream.Mode.decode(parse('bytes'))
Mode.bytes()
>>> bundle.stream.Mode.decode(parse('lf'))
Mode.lines(LineMode.lf())
>>> bundle.stream.Mode.decode(parse('<packet 123>'))
Mode.packet {'size': 123}
>>> bundle.stream.Mode.decode(parse('<object "?">'))
Mode.object {'description': '?'}

```

Invalid input causes [SchemaDecodeFailed][preserves.schema.SchemaDecodeFailed] to be raised:

```python
>>> bundle.stream.Mode.decode(parse('<i-am-not-a-valid-mode>'))
Traceback (most recent call last):
  ...
preserves.schema.SchemaDecodeFailed: Could not decode <i-am-not-a-valid-mode> using <class 'stream.Mode'>
Most likely reason: in stream.LineMode.crlf: <lit crlf> didn't match <i-am-not-a-valid-mode>
Full explanation: 
  in stream.Mode: matching <i-am-not-a-valid-mode>
    in stream.Mode.bytes: <lit bytes> didn't match <i-am-not-a-valid-mode>
    in stream.Mode.lines: <ref [] LineMode> didn't match <i-am-not-a-valid-mode>
      in stream.LineMode: matching <i-am-not-a-valid-mode>
        in stream.LineMode.lf: <lit lf> didn't match <i-am-not-a-valid-mode>
        in stream.LineMode.crlf: <lit crlf> didn't match <i-am-not-a-valid-mode>
    in stream.Mode.packet: <lit packet> didn't match i-am-not-a-valid-mode
    in stream.Mode.object: <lit object> didn't match i-am-not-a-valid-mode

```

The "full explanation" includes details on which parses were attempted, and why they failed.

Again, the [try_decode][preserves.schema.SchemaObject.try_decode] method catches
[SchemaDecodeFailed][preserves.schema.SchemaDecodeFailed], transforming it into `None`:

```python
>>> bundle.stream.Mode.try_decode(parse('bytes'))
Mode.bytes()
>>> bundle.stream.Mode.try_decode(parse('<i-am-not-a-valid-mode>'))

```

Direct instantiation is done with the variant classes, not with `Mode` itself:

```python
>>> bundle.stream.Mode.bytes()
Mode.bytes()
>>> bundle.stream.Mode.lines(bundle.stream.LineMode.lf())
Mode.lines(LineMode.lf())
>>> bundle.stream.Mode.packet(123)
Mode.packet {'size': 123}
>>> bundle.stream.Mode.object('?')
Mode.object {'description': '?'}

```

Fields and contents can be queried as usual:

```python
>>> bundle.stream.Mode.lines(bundle.stream.LineMode.lf()).value
LineMode.lf()
>>> bundle.stream.Mode.packet(123).size
123
>>> bundle.stream.Mode.object('?').description
'?'

```

And serialization and encoding are also as expected:

```python
>>> print(stringify(bundle.stream.Mode.bytes()))
bytes
>>> print(stringify(bundle.stream.Mode.lines(bundle.stream.LineMode.lf())))
lf
>>> print(stringify(bundle.stream.Mode.packet(123)))
<packet 123>
>>> print(stringify(bundle.stream.Mode.object('?')))
<object "?">
>>> canonicalize(bundle.stream.Mode.object('?'))
b'\\xb4\\xb3\\x06object\\xb1\\x01?\\x84'

```

Finally, the [VARIANT][preserves.schema.SchemaObject.VARIANT] attribute of instances
allows code to dispatch on what kind of data it is handling at a given moment:

```python
>>> bundle.stream.Mode.bytes().VARIANT
#bytes
>>> bundle.stream.Mode.lines(bundle.stream.LineMode.lf()).VARIANT
#lines
>>> bundle.stream.Mode.packet(123).VARIANT
#packet
>>> bundle.stream.Mode.object('?').VARIANT
#object

```

"""

from . import *
import pathlib
import keyword
from functools import wraps

AND = Symbol('and')
ANY = Symbol('any')
ATOM = Symbol('atom')
BOOLEAN = Symbol('Boolean')
BUNDLE = Symbol('bundle')
BYTE_STRING = Symbol('ByteString')
DEFINITIONS = Symbol('definitions')
DICT = Symbol('dict')
DICTOF = Symbol('dictof')
DOUBLE = Symbol('Double')
EMBEDDED = Symbol('embedded')
LIT = Symbol('lit')
NAMED = Symbol('named')
OR = Symbol('or')
REC = Symbol('rec')
REF = Symbol('ref')
SCHEMA = Symbol('schema')
SEQOF = Symbol('seqof')
SETOF = Symbol('setof')
SIGNED_INTEGER = Symbol('SignedInteger')
STRING = Symbol('String')
SYMBOL = Symbol('Symbol')
TUPLE = Symbol('tuple')
TUPLE_PREFIX = Symbol('tuplePrefix')
VERSION = Symbol('version')

def sequenceish(x):
    return isinstance(x, tuple) or isinstance(x, list)

class SchemaDecodeFailed(ValueError):
    """Raised when [decode][preserves.schema.SchemaObject.decode] cannot find a way to parse a
    given input.

    Attributes:
        cls (class): the SchemaObject subclass attempting the parse
        pattern (Value): the failing pattern, a `Value` conforming to schema `meta.Pattern`
        value (Value): the unparseable value
        failures (list[SchemaDecodeFailed]): descriptions of failed paths attempted during the match this failure describes
    """
    def __init__(self, cls, p, v, failures=None):
        super().__init__()
        self.cls = cls
        self.pattern = p
        self.value = v
        self.failures = [] if failures is None else failures

    def __str__(self):
        b = ExplanationBuilder()
        return f'Could not decode {b.truncated(stringify(self.value))} using {self.cls}' + \
            b.explain(self)

class ExplanationBuilder:
    INDENT = 2
    def __init__(self):
        self.indentLevel = self.INDENT
        self.deepest_failure = (-1, None)

    def truncated(self, s):
        return s[:36] + ' ...' if len(s) > 40 else s

    def explain(self, failure):
        tree = self._tree(failure)
        deepest = self.deepest_failure[1]
        if deepest is None:
            return tree
        else:
            return f'\nMost likely reason: {self._node(deepest)}\nFull explanation: {tree}'

    def _node(self, failure):
        pexp = ' matching' if failure.pattern is None else f' {stringify(failure.pattern)} didn\'t match'
        c = failure.cls.__module__ + '.' + failure.cls.__qualname__
        return f'in {c}:{pexp} {self.truncated(stringify(failure.value))}'

    def _tree(self, failure):
        if self.indentLevel >= self.deepest_failure[0]:
            self.deepest_failure = (self.indentLevel, failure)
        self.indentLevel += self.INDENT
        nested = [self._tree(f) for f in failure.failures]
        self.indentLevel -= self.INDENT
        return '\n' + ' ' * self.indentLevel + self._node(failure) + ''.join(nested)

class SchemaObject:
    """Base class for classes representing grammatical productions in a schema: instances of
    [SchemaObject][preserves.schema.SchemaObject] represent schema *definitions*. This is an
    abstract class, as are its subclasses [Enumeration][preserves.schema.Enumeration] and
    [Definition][preserves.schema.Definition]. It is subclasses of *those* subclasses,
    automatically produced during schema loading, that are actually instantiated.

    ```python
    >>> bundle = load_schema_file('docs/syndicate-protocols-schema-bundle.bin')

    >>> bundle.stream.Mode.mro()[1:-1]
    [<class 'preserves.schema.Enumeration'>, <class 'preserves.schema.SchemaObject'>]

    >>> bundle.stream.Mode.packet.mro()[1:-1]
    [<class 'stream.Mode._ALL'>, <class 'preserves.schema.Definition'>, <class 'preserves.schema.SchemaObject'>]

    >>> bundle.stream.StreamListenerError.mro()[1:-1]
    [<class 'preserves.schema.Definition'>, <class 'preserves.schema.SchemaObject'>]

    ```

    Illustrating the class attributes on [SchemaObject][preserves.schema.SchemaObject]
    subclasses:

    ```python
    >>> bundle.stream.Mode.ROOTNS is bundle
    True

    >>> print(stringify(bundle.stream.Mode.SCHEMA, indent=2))
    <or [
      [
        "bytes"
        <lit bytes>
      ]
      [
        "lines"
        <ref [] LineMode>
      ]
      [
        "packet"
        <rec <lit packet> <tuple [<named size <atom SignedInteger>>]>>
      ]
      [
        "object"
        <rec <lit object> <tuple [<named description any>]>>
      ]
    ]>

    >>> bundle.stream.Mode.MODULE_PATH
    (#stream,)

    >>> bundle.stream.Mode.NAME
    #Mode

    >>> bundle.stream.Mode.VARIANT is None
    True
    >>> bundle.stream.Mode.packet.VARIANT
    #packet

    ```

    """

    ROOTNS = None
    """A [Namespace][preserves.schema.Namespace] that is the top-level environment for all
    bundles included in the [Compiler][preserves.schema.Compiler] run that produced this
    [SchemaObject][preserves.schema.SchemaObject].

    """

    SCHEMA = None
    """A `Value` conforming to schema `meta.Definition` (and thus often to `meta.Pattern`
    etc.), interpreted by the [SchemaObject][preserves.schema.SchemaObject] machinery to drive
    parsing, unparsing and so forth."""

    MODULE_PATH = None
    """A sequence (tuple) of [Symbol][preserves.values.Symbol]s naming the path from the root
    to the schema module containing this definition."""

    NAME = None
    """A [Symbol][preserves.values.Symbol] naming this definition within its module."""

    VARIANT = None
    """`None` for [Definition][preserves.schema.Definition]s (such as
    `bundle.stream.StreamListenerError` above) and for overall
    [Enumeration][preserves.schema.Enumeration]s (such as `bundle.stream.Mode`), or a
    [Symbol][preserves.values.Symbol] for variant definitions *contained within* an enumeration
    (such as `bundle.stream.Mode.packet`).

    """

    @classmethod
    def decode(cls, v):
        """Parses `v` using the [SCHEMA][preserves.schema.SchemaObject.SCHEMA], returning a
        (sub)instance of [SchemaObject][preserves.schema.SchemaObject] or raising
        [SchemaDecodeFailed][preserves.schema.SchemaDecodeFailed]."""
        raise NotImplementedError('Subclass responsibility')

    @classmethod
    def try_decode(cls, v):
        """Parses `v` using the [SCHEMA][preserves.schema.SchemaObject.SCHEMA], returning a
        (sub)instance of [SchemaObject][preserves.schema.SchemaObject] or `None` if parsing
        failed."""
        try:
            return cls.decode(v)
        except SchemaDecodeFailed:
            return None

    @classmethod
    def parse(cls, p, v, args):
        if p == ANY:
            return v
        if p.key == NAMED:
            i = cls.parse(p[1], v, args)
            args.append(i)
            return i
        if p.key == ATOM:
            k = p[0]
            if k == BOOLEAN and isinstance(v, bool): return v
            if k == DOUBLE and isinstance(v, float): return v
            if k == SIGNED_INTEGER and isinstance(v, int): return v
            if k == STRING and isinstance(v, str): return v
            if k == BYTE_STRING and isinstance(v, bytes): return v
            if k == SYMBOL and isinstance(v, Symbol): return v
            raise SchemaDecodeFailed(cls, p, v)
        if p.key == EMBEDDED:
            if not isinstance(v, Embedded): raise SchemaDecodeFailed(cls, p, v)
            return v.embeddedValue
        if p.key == LIT:
            if v == p[0]: return ()
            raise SchemaDecodeFailed(cls, p, v)
        if p.key == SEQOF:
            if not sequenceish(v): raise SchemaDecodeFailed(cls, p, v)
            return [cls.parse(p[0], w, args) for w in v]
        if p.key == SETOF:
            if not isinstance(v, set): raise SchemaDecodeFailed(cls, p, v)
            return set(cls.parse(p[0], w, args) for w in v)
        if p.key == DICTOF:
            if not isinstance(v, dict): raise SchemaDecodeFailed(cls, p, v)
            return dict((cls.parse(p[0], k, args), cls.parse(p[1], w, args))
                        for (k, w) in v.items())
        if p.key == REF:
            c = lookup(cls.ROOTNS, cls.MODULE_PATH if len(p[0]) == 0 else p[0], p[1])
            failure = None
            try:
                return c.decode(v)
            except SchemaDecodeFailed as exn:
                failure = exn
            raise SchemaDecodeFailed(cls, p, v, [failure])
        if p.key == REC:
            if not isinstance(v, Record): raise SchemaDecodeFailed(cls, p, v)
            cls.parse(p[0], v.key, args)
            cls.parse(p[1], v.fields, args)
            return ()
        if p.key == TUPLE:
            if not sequenceish(v): raise SchemaDecodeFailed(cls, p, v)
            if len(v) < len(p[0]): raise SchemaDecodeFailed(cls, p, v)
            i = 0
            for pp in p[0]:
                cls.parse(pp, v[i], args)
                i = i + 1
            return ()
        if p.key == TUPLE_PREFIX:
            if not sequenceish(v): raise SchemaDecodeFailed(cls, p, v)
            if len(v) < len(p[0]): raise SchemaDecodeFailed(cls, p, v)
            i = 0
            for pp in p[0]:
                cls.parse(pp, v[i], args)
                i = i + 1
            cls.parse(p[1], v[i:], args)
            return ()
        if p.key == DICT:
            if not isinstance(v, dict): raise SchemaDecodeFailed(cls, p, v)
            if len(v) < len(p[0]): raise SchemaDecodeFailed(cls, p, v)
            for (k, pp) in compare.sorted_items(p[0]):
                if k not in v: raise SchemaDecodeFailed(cls, p, v)
                cls.parse(pp, v[k], args)
            return ()
        if p.key == AND:
            for pp in p[0]:
                cls.parse(pp, v, args)
            return ()
        raise ValueError(f'Bad schema {p}')

    def __preserve__(self):
        """Called by [preserves.values.preserve][]: *unparses* the information represented by
        this instance, using its schema definition, to produce a Preserves `Value`."""
        raise NotImplementedError('Subclass responsibility')

    def __repr__(self):
        n = self._constructor_name()
        if self.SIMPLE:
            if self.EMPTY:
                return n + '()'
            else:
                return n + '(' + repr(self.value) + ')'
        else:
            return n + ' ' + repr(self._as_dict())

    def _as_dict(self):
        raise NotImplementedError('Subclass responsibility')

class Enumeration(SchemaObject):
    """Subclasses of [Enumeration][preserves.schema.Enumeration] represent a group of variant
    options within a sum type.

    ```python
    >>> bundle = load_schema_file('docs/syndicate-protocols-schema-bundle.bin')

    >>> import pprint
    >>> pprint.pprint(bundle.stream.Mode.VARIANTS)
    [(#bytes, <class 'stream.Mode.bytes'>),
     (#lines, <class 'stream.Mode.lines'>),
     (#packet, <class 'stream.Mode.packet'>),
     (#object, <class 'stream.Mode.object'>)]

    >>> bundle.stream.Mode.VARIANTS[0][1] is bundle.stream.Mode.bytes
    True

    ```

    """

    VARIANTS = None
    """List of `(Symbol, SchemaObject class)` tuples representing the possible options within
    this sum type."""

    def __init__(self):
        raise TypeError('Cannot create instance of Enumeration')

    @classmethod
    def _set_schema(cls, rootns, module_path, name, schema, _variant, _enumeration):
        cls.ROOTNS = rootns
        cls.SCHEMA = schema
        cls.MODULE_PATH = module_path
        cls.NAME = name
        cls.VARIANTS = []
        cls._ALL = pretty_subclass(Definition, module_path_str(module_path + (name,)), '_ALL')
        for (n, d) in schema[0]:
            n = Symbol(n)
            c = pretty_subclass(cls._ALL, module_path_str(module_path + (name,)), n.name)
            c._set_schema(rootns, module_path, name, d, n, cls)
            cls.VARIANTS.append((n, c))
            safesetattr(cls, n.name, c)

    @classmethod
    def decode(cls, v):
        failures = None
        for (n, c) in cls.VARIANTS:
            try:
                return c.decode(v)
            except SchemaDecodeFailed as failure:
                if failures is None: failures = []
                failures.append(failure)
        raise SchemaDecodeFailed(cls, None, v, failures)

    def __preserve__(self):
        raise TypeError('Cannot encode instance of Enumeration')

def safeattrname(k):
    """Escapes Python keywords by prepending `_`; passes all other strings through."""
    return k + '_' if keyword.iskeyword(k) else k

def safesetattr(o, k, v):
    setattr(o, safeattrname(k), v)

def safegetattr(o, k):
    return getattr(o, safeattrname(k))

def safehasattr(o, k):
    return hasattr(o, safeattrname(k))

class Definition(SchemaObject):
    """Subclasses of [Definition][preserves.schema.Definition] are used to represent both
    standalone non-alternation definitions as well as alternatives within an
    [Enumeration][preserves.schema.Enumeration].

    ```python
    >>> bundle = load_schema_file('docs/syndicate-protocols-schema-bundle.bin')

    >>> bundle.stream.StreamListenerError.FIELD_NAMES
    ['spec', 'message']
    >>> bundle.stream.StreamListenerError.SAFE_FIELD_NAMES
    ['spec', 'message']
    >>> bundle.stream.StreamListenerError.ENUMERATION is None
    True

    >>> bundle.stream.Mode.object.FIELD_NAMES
    ['description']
    >>> bundle.stream.Mode.object.SAFE_FIELD_NAMES
    ['description']
    >>> bundle.stream.Mode.object.ENUMERATION is bundle.stream.Mode
    True

    >>> bundle.stream.CreditAmount.count.FIELD_NAMES
    []
    >>> bundle.stream.CreditAmount.count.SAFE_FIELD_NAMES
    []
    >>> bundle.stream.CreditAmount.count.ENUMERATION is bundle.stream.CreditAmount
    True

    >>> bundle.stream.CreditAmount.decode(parse('123'))
    CreditAmount.count(123)
    >>> bundle.stream.CreditAmount.count(123)
    CreditAmount.count(123)
    >>> bundle.stream.CreditAmount.count(123).value
    123

    ```

    """

    EMPTY = False
    SIMPLE = False

    FIELD_NAMES = []
    """List of strings: names of the fields contained within this definition, if it has named
    fields at all; otherwise, an empty list, and the definition is a simple wrapper for another
    value, in which case that value is accessed via the `value` attribute."""

    SAFE_FIELD_NAMES = []
    """The list produced by mapping [safeattrname][preserves.schema.safeattrname] over
    [FIELD_NAMES][preserves.schema.Definition.FIELD_NAMES]."""

    ENUMERATION = None
    """`None` for standalone top-level definitions with a module; otherwise, an
    [Enumeration][preserves.schema.Enumeration] subclass representing a top-level alternation
    definition."""

    def _constructor_name(self):
        if self.VARIANT is None:
            return self.NAME.name
        else:
            return self.NAME.name + '.' + self.VARIANT.name

    def __init__(self, *args, **kwargs):
        self._fields = args
        if self.SIMPLE:
            if self.EMPTY:
                if len(args) != 0:
                    raise TypeError('%s takes no arguments' % (self._constructor_name(),))
            else:
                if len(args) != 1:
                    raise TypeError('%s needs exactly one argument' % (self._constructor_name(),))
                self.value = args[0]
        else:
            i = 0
            for arg in args:
                if i >= len(self.FIELD_NAMES):
                    raise TypeError('%s given too many positional arguments' % (self._constructor_name(),))
                setattr(self, self.SAFE_FIELD_NAMES[i], arg)
                i = i + 1
            for (argname, arg) in kwargs.items():
                if hasattr(self, argname):
                    raise TypeError('%s given duplicate attribute: %r' % (self._constructor_name, argname))
                if argname not in self.SAFE_FIELD_NAMES:
                    raise TypeError('%s given unknown attribute: %r' % (self._constructor_name, argname))
                setattr(self, argname, arg)
                i = i + 1
            if i != len(self.FIELD_NAMES):
                raise TypeError('%s needs argument(s) %r' % (self._constructor_name(), self.FIELD_NAMES))

    def __eq__(self, other):
        return (other.__class__ is self.__class__) and (self._fields == other._fields)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._fields) ^ hash(self.__class__)

    def _accept(self, visitor):
        if self.VARIANT is None:
            return visitor(*self._fields)
        else:
            return visitor[self.VARIANT.name](*self._fields)

    @classmethod
    def _set_schema(cls, rootns, module_path, name, schema, variant, enumeration):
        cls.ROOTNS = rootns
        cls.SCHEMA = schema
        cls.MODULE_PATH = module_path
        cls.NAME = name
        cls.EMPTY = is_empty_pattern(schema)
        cls.SIMPLE = is_simple_pattern(schema)
        cls.FIELD_NAMES = []
        cls.VARIANT = variant
        cls.ENUMERATION = enumeration
        gather_defined_field_names(schema, cls.FIELD_NAMES)
        cls.SAFE_FIELD_NAMES = [safeattrname(n) for n in cls.FIELD_NAMES]

    @classmethod
    def decode(cls, v):
        if cls.SIMPLE:
            i = cls.parse(cls.SCHEMA, v, [])
            if cls.EMPTY:
                return cls()
            else:
                return cls(i)
        else:
            args = []
            cls.parse(cls.SCHEMA, v, args)
            return cls(*args)

    def __preserve__(self):
        if self.SIMPLE:
            if self.EMPTY:
                return encode(self.SCHEMA, ())
            else:
                return encode(self.SCHEMA, self.value)
        else:
            return encode(self.SCHEMA, self)

    def _as_dict(self):
        return dict((k, safegetattr(self, k)) for k in self.FIELD_NAMES)

    def __getitem__(self, name):
        return safegetattr(self, name)

    def __setitem__(self, name, value):
        return safesetattr(self, name, value)

class escape:
    def __init__(self, escaped):
        self.escaped = escaped
    def __escape_schema__(self):
        return self.escaped

def encode(p, v):
    if hasattr(v, '__escape_schema__'):
        return preserve(v.__escape_schema__())
    if p == ANY:
        return v
    if p.key == NAMED:
        return encode(p[1], safegetattr(v, p[0].name))
    if p.key == ATOM:
        return v
    if p.key == EMBEDDED:
        return Embedded(v)
    if p.key == LIT:
        return p[0]
    if p.key == SEQOF:
        return tuple(encode(p[0], w) for w in v)
    if p.key == SETOF:
        return set(encode(p[0], w) for w in v)
    if p.key == DICTOF:
        return dict((encode(p[0], k), encode(p[1], w)) for (k, w) in v.items())
    if p.key == REF:
        return preserve(v)
    if p.key == REC:
        return Record(encode(p[0], v), encode(p[1], v))
    if p.key == TUPLE:
        return tuple(encode(pp, v) for pp in p[0])
    if p.key == TUPLE_PREFIX:
        return tuple(encode(pp, v) for pp in p[0]) + encode(p[1], v)
    if p.key == DICT:
        return dict((k, encode(pp, v)) for (k, pp) in p[0].items())
    if p.key == AND:
        return merge(*[encode(pp, v) for pp in p[0]])
    raise ValueError(f'Bad schema {p}')

def module_path_str(mp):
    return '.'.join([e.name for e in mp])

SIMPLE_PATTERN_KEYS = [ATOM, EMBEDDED, LIT, SEQOF, SETOF, DICTOF, REF]
def is_simple_pattern(p):
    return p == ANY or (isinstance(p, Record) and p.key in SIMPLE_PATTERN_KEYS)

def is_empty_pattern(p):
    return isinstance(p, Record) and p.key == LIT

def gather_defined_field_names(s, acc):
    if is_simple_pattern(s):
        pass
    elif sequenceish(s):
        for p in s:
            gather_defined_field_names(p, acc)
    elif s.key == NAMED:
        acc.append(s[0].name)
        gather_defined_field_names(s[1], acc)
    elif s.key == AND:
        gather_defined_field_names(s[0], acc)
    elif s.key == REC:
        gather_defined_field_names(s[0], acc)
        gather_defined_field_names(s[1], acc)
    elif s.key == TUPLE:
        gather_defined_field_names(s[0], acc)
    elif s.key == TUPLE_PREFIX:
        gather_defined_field_names(s[0], acc)
        gather_defined_field_names(s[1], acc)
    elif s.key == DICT:
        gather_defined_field_names(tuple(item[1] for item in compare.sorted_items(s[0])), acc)
    else:
        raise ValueError('Bad schema')

def pretty_subclass(C, module_name, class_name):
    class S(C): pass
    S.__module__ = module_name
    S.__name__ = class_name
    S.__qualname__ = class_name
    return S

def lookup(ns, module_path, name):
    for e in module_path:
        if e not in ns:
            definition_not_found(module_path, name)
        ns = ns[e]
    if name not in ns:
        definition_not_found(module_path, name)
    return ns[name]

def definition_not_found(module_path, name):
    raise KeyError('Definition not found: ' + module_path_str(module_path + (name,)))

class Namespace:
    """A [Namespace][preserves.schema.Namespace] is a dictionary-like object representing a
    schema module that knows its location in a schema module hierarchy and whose attributes
    correspond to definitions and submodules within the schema module.

    Attributes:
        _prefix (tuple[Symbol]): path to this module/Namespace from the root Namespace
    """
    def __init__(self, prefix):
        self._prefix = prefix

    def __getitem__(self, name):
        return safegetattr(self, Symbol(name).name)

    def __setitem__(self, name, value):
        name = Symbol(name).name
        if name in self.__dict__:
            raise ValueError('Name conflict: ' + module_path_str(self._prefix + (name,)))
        safesetattr(self, name, value)

    def __contains__(self, name):
        return safeattrname(Symbol(name).name) in self.__dict__

    def _items(self):
        return dict((k, v) for (k, v) in self.__dict__.items() if k[0] != '_')

    def __repr__(self):
        return repr(self._items())

class Compiler:
    """Instances of [Compiler][preserves.schema.Compiler] populate an initially-empty
    [Namespace][preserves.schema.Namespace] by loading and compiling schema bundle files.

    ```python
    >>> c = Compiler()
    >>> c.load('docs/syndicate-protocols-schema-bundle.bin')
    >>> type(c.root)
    <class 'preserves.schema.Namespace'>

    ```

    Attributes:
        root (Namespace): the root namespace into which top-level schema modules are installed.
    """
    def __init__(self):
        self.root = Namespace(())

    def load_filelike(self, f, module_name=None):
        """Reads a `meta.Bundle` or `meta.Schema` from the filelike object `f`, compiling and
        installing it in `self.root`. If `f` contains a bundle, `module_name` is not used,
        since the schema modules in the bundle know their own names; if `f` contains a plain
        schema module, however, `module_name` is used directly if it is a string, and if it is
        `None`, a suitable module name is computed from the `name` attribute of `f`, if it is
        present. If `name` is absent in that case, `ValueError` is raised.

        """
        x = Decoder(f.read()).next()
        if x.key == SCHEMA:
            if module_name is None:
                if hasattr(f, 'name'):
                    module_name = pathlib.Path(f.name).stem
                else:
                    raise ValueError('Cannot load schema module from filelike object without a module_name')
            self.load_schema((Symbol(module_name),), x)
        elif x.key == BUNDLE:
            for (p, s) in x[0].items():
                self.load_schema(p, s)

    def load(self, filename):
        """Opens the file at `filename`, passing the resulting file object to
        [load_filelike][preserves.schema.Compiler.load_filelike]."""
        filename = pathlib.Path(filename)
        with open(filename, 'rb') as f:
            self.load_filelike(f, filename.stem)

    def load_schema(self, module_path, schema):
        if schema[0][VERSION] != 1:
            raise NotImplementedError('Unsupported Schema version')
        ns = self.root
        for e in module_path:
            if not e in ns:
                ns[e] = Namespace(ns._prefix + (e,))
            ns = ns[e]
        for (n, d) in schema[0][DEFINITIONS].items():
            if isinstance(d, Record) and d.key == OR:
                superclass = Enumeration
            else:
                superclass = Definition
            c = pretty_subclass(superclass, module_path_str(module_path), n.name)
            c._set_schema(self.root, module_path, n, d, None, None)
            ns[n] = c

def load_schema_file(filename):
    """Simple entry point to the compiler: creates a [Compiler][preserves.schema.Compiler],
    calls [load][preserves.schema.Compiler.load] on it, and returns its `root`
    [Namespace][preserves.schema.Namespace].

    ```python
    >>> bundle = load_schema_file('docs/syndicate-protocols-schema-bundle.bin')
    >>> type(bundle)
    <class 'preserves.schema.Namespace'>

    ```
    """
    c = Compiler()
    c.load(filename)
    return c.root

# a decorator
def extend(cls):
    """A decorator for function definitions. Useful for adding *behaviour* to the classes
    resulting from loading a schema module:

    ```python
    >>> bundle = load_schema_file('docs/syndicate-protocols-schema-bundle.bin')

    >>> @extend(bundle.stream.LineMode.lf)
    ... def what_am_i(self):
    ...     return 'I am a LINEFEED linemode'

    >>> @extend(bundle.stream.LineMode.crlf)
    ... def what_am_i(self):
    ...     return 'I am a CARRIAGE-RETURN-PLUS-LINEFEED linemode'

    >>> bundle.stream.LineMode.lf()
    LineMode.lf()
    >>> bundle.stream.LineMode.lf().what_am_i()
    'I am a LINEFEED linemode'

    >>> bundle.stream.LineMode.crlf()
    LineMode.crlf()
    >>> bundle.stream.LineMode.crlf().what_am_i()
    'I am a CARRIAGE-RETURN-PLUS-LINEFEED linemode'

    ```

    """
    @wraps(cls)
    def extender(f):
        setattr(cls, f.__name__, f)
        return f
    return extender

__metaschema_filename = pathlib.Path(__file__).parent / 'schema.prb'
meta = load_schema_file(__metaschema_filename).schema
"""Schema module [Namespace][preserves.schema.Namespace] corresponding to [Preserves Schema's
metaschema](https://preserves.dev/preserves-schema.html#appendix-metaschema)."""

if __name__ == '__main__':
    with open(__metaschema_filename, 'rb') as f:
        x = Decoder(f.read()).next()
    print(meta.Schema.decode(x))
    print(preserve(meta.Schema.decode(x)))
    assert preserve(meta.Schema.decode(x)) == x

    @extend(meta.Schema)
    def f(self, x):
        return ['yay', self.embeddedType, x]
    print(meta.Schema.decode(x).f(123))
    print(f)

    print()

    path_bin_filename = pathlib.Path(__file__).parent / 'path.prb'
    path = load_schema_file(path_bin_filename).path
    with open(path_bin_filename, 'rb') as f:
        x = Decoder(f.read()).next()
    print(meta.Schema.decode(x))
    assert meta.Schema.decode(x) == meta.Schema.decode(x)
    assert preserve(meta.Schema.decode(x)) == x

    print()
    print(path)
