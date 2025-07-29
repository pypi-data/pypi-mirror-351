"""The [preserves.values][] module implements the core representations of Preserves
[`Value`s](https://preserves.dev/preserves.html#semantics) as Python values.

"""

import re
import sys
import struct
import math

from .error import DecodeError

def preserve(v):
    """Converts `v` to a representation of a Preserves `Value` by (repeatedly) setting

    ```python
    v = v.__preserve__()
    ```

    while `v` has a `__preserve__` method. Parsed [Schema][preserves.schema]
    values are able to render themselves to their serialized representations this way.

    """
    while hasattr(v, '__preserve__'):
        v = v.__preserve__()
    return v

def float_to_int(v):
    return struct.unpack('>Q', struct.pack('>d', v))[0]

def cmp_floats(a, b):
    """Implements the `totalOrder` predicate defined in section 5.10 of [IEEE Std
    754-2008](https://dx.doi.org/10.1109/IEEESTD.2008.4610935).

    """
    a = float_to_int(a)
    b = float_to_int(b)
    if a & 0x8000000000000000: a = a ^ 0x7fffffffffffffff
    if b & 0x8000000000000000: b = b ^ 0x7fffffffffffffff
    return a - b

# FIXME: This regular expression is conservatively correct, but Anglo-chauvinistic.
RAW_SYMBOL_RE = re.compile(r'^[-a-zA-Z0-9~!$%^&*?_=+/.|]+$')

def _eq(a, b):
    from .compare import eq
    return eq(a, b)

class Symbol(object):
    """Representation of Preserves `Symbol`s.

    ```python
    >>> Symbol('xyz')
    #xyz
    >>> Symbol('xyz').name
    'xyz'
    >>> repr(Symbol('xyz'))
    '#xyz'
    >>> str(Symbol('xyz'))
    'xyz'
    >>> import preserves
    >>> preserves.stringify(Symbol('xyz'))
    'xyz'
    >>> preserves.stringify(Symbol('hello world'))
    "'hello world'"
    >>> preserves.parse('xyz')
    #xyz
    >>> preserves.parse("'hello world'")
    #hello world

    ```

    Attributes:
        name (str | Symbol):
            The symbol's text label. If an existing [Symbol][preserves.values.Symbol] is passed
            in, the existing Symbol's `name` is used as the `name` for the new Symbol.
    """
    def __init__(self, name):
        self.name = name.name if isinstance(name, Symbol) else name

    def __eq__(self, other):
        other = _unwrap(other)
        return isinstance(other, Symbol) and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.name < other.name

    def __le__(self, other):
        return self.name <= other.name

    def __gt__(self, other):
        return self.name > other.name

    def __ge__(self, other):
        return self.name >= other.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return '#' + self.name

    def __str__(self):
        return self.name

    def __preserve_write_binary__(self, encoder):
        bs = self.name.encode('utf-8')
        encoder.buffer.append(0xb3)
        encoder.varint(len(bs))
        encoder.buffer.extend(bs)

    def __preserve_write_text__(self, formatter):
        if RAW_SYMBOL_RE.match(self.name):
            formatter.chunks.append(self.name)
        else:
            formatter.chunks.append("'")
            for c in self.name:
                if c == "'": formatter.chunks.append("\\'")
                else: formatter.write_stringlike_char(c)
            formatter.chunks.append("'")

class Record(object):
    """Representation of Preserves `Record`s, which are a pair of a *label* `Value` and a sequence of *field* `Value`s.

    ```python
    >>> r = Record(Symbol('label'), ['field1', ['field2item1', 'field2item2']])
    >>> r
    #label('field1', ['field2item1', 'field2item2'])
    >>> r.key
    #label
    >>> r.fields
    ('field1', ['field2item1', 'field2item2'])
    >>> import preserves
    >>> preserves.stringify(r)
    '<label "field1" ["field2item1" "field2item2"]>'
    >>> r == preserves.parse('<label "field1" ["field2item1" "field2item2"]>')
    True

    ```

    Args:
        key (Value): the `Record`'s label
        fields (iterable[Value]): the fields of the `Record`

    Attributes:
        key (Value): the `Record`'s label
        fields (tuple[Value]): the fields of the `Record`
    """
    def __init__(self, key, fields):
        self.key = key
        self.fields = tuple(fields)
        self.__hash = None

    def __eq__(self, other):
        other = _unwrap(other)
        return isinstance(other, Record) and _eq((self.key, self.fields), (other.key, other.fields))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        if self.__hash is None:
            self.__hash = hash((self.key, self.fields))
        return self.__hash

    def __repr__(self):
        return repr(self.key) + '(' + ', '.join((repr(f) for f in self.fields)) + ')'

    def __preserve_write_binary__(self, encoder):
        encoder.buffer.append(0xb4)
        encoder.append(self.key)
        for f in self.fields:
            encoder.append(f)
        encoder.buffer.append(0x84)

    def __preserve_write_text__(self, formatter):
        formatter.chunks.append('<')
        formatter.append(self.key)
        for f in self.fields:
            formatter.chunks.append(' ')
            formatter.append(f)
        formatter.chunks.append('>')

    def __getitem__(self, index):
        return self.fields[index]

    @staticmethod
    def makeConstructor(labelSymbolText, fieldNames):
        """
        Equivalent to `Record.makeBasicConstructor(Symbol(labelSymbolText), fieldNames)`.

        Deprecated:
           Use [preserves.schema][] definitions instead.
        """
        return Record.makeBasicConstructor(Symbol(labelSymbolText), fieldNames)

    @staticmethod
    def makeBasicConstructor(label, fieldNames):
        """Constructs and returns a "constructor" for `Record`s having a certain `label` and
        number of fields.

        Deprecated:
           Use [preserves.schema][] definitions instead.

        The "constructor" is a callable function that accepts `len(fields)` arguments and
        returns a [Record][preserves.values.Record] with `label` as its label and the arguments
        to the constructor as field values.

        In addition, the "constructor" has a `constructorInfo` attribute holding a
        [RecordConstructorInfo][preserves.values.RecordConstructorInfo] object, an `isClassOf`
        attribute holding a unary function that returns `True` iff its argument is a
        [Record][preserves.values.Record] with label `label` and arity `len(fieldNames)`, and
        an `ensureClassOf` attribute that raises an `Exception` if `isClassOf` returns false on
        its argument and returns the argument otherwise.

        Finally, for each field name `f` in `fieldNames`, the "constructor" object has an
        attribute `_f` that is a unary function that retrieves the `f` field from the passed in
        argument.

        ```python
        >>> c = Record.makeBasicConstructor(Symbol('date'), 'year month day')
        >>> c(1969, 7, 16)
        #date(1969, 7, 16)
        >>> c.constructorInfo
        #date/3
        >>> c.isClassOf(c(1969, 7, 16))
        True
        >>> c.isClassOf(Record(Symbol('date'), [1969, 7, 16]))
        True
        >>> c.isClassOf(Record(Symbol('date'), [1969]))
        False
        >>> c.ensureClassOf(c(1969, 7, 16))
        #date(1969, 7, 16)
        >>> c.ensureClassOf(Record(Symbol('date'), [1969]))
        Traceback (most recent call last):
          ...
        TypeError: Record: expected #date/3, got #date(1969)
        >>> c._year(c(1969, 7, 16))
        1969
        >>> c._month(c(1969, 7, 16))
        7
        >>> c._day(c(1969, 7, 16))
        16

        ```

        Args:
            label (Value): Label to use for constructed/matched `Record`s
            fieldNames (tuple[str] | list[str] | str): Names of the `Record`'s fields

        """
        if type(fieldNames) == str:
            fieldNames = fieldNames.split()
        arity = len(fieldNames)
        def ctor(*fields):
            if len(fields) != arity:
                raise Exception("Record: cannot instantiate %r expecting %d fields with %d fields"%(
                    label,
                    arity,
                    len(fields)))
            return Record(label, fields)
        ctor.constructorInfo = RecordConstructorInfo(label, arity)
        ctor.isClassOf = lambda v: \
                         isinstance(v, Record) and v.key == label and len(v.fields) == arity
        def ensureClassOf(v):
            if not ctor.isClassOf(v):
                raise TypeError("Record: expected %r/%d, got %r" % (label, arity, v))
            return v
        ctor.ensureClassOf = ensureClassOf
        for fieldIndex in range(len(fieldNames)):
            fieldName = fieldNames[fieldIndex]
            # Stupid python scoping bites again
            def getter(fieldIndex):
                return lambda v: ensureClassOf(v)[fieldIndex]
            setattr(ctor, '_' + fieldName, getter(fieldIndex))
        return ctor

class RecordConstructorInfo(object):
    """Describes the shape of a `Record` constructor, namely its *label* and its *arity* (field
    count).

    ```python
    >>> RecordConstructorInfo(Symbol('label'), 3)
    #label/3

    ```

    Attributes:
        key (Value): the label of matching `Record`s
        arity (int): the number of fields in matching `Record`s
    """
    def __init__(self, key, arity):
        self.key = key
        self.arity = arity

    def __eq__(self, other):
        other = _unwrap(other)
        return isinstance(other, RecordConstructorInfo) and \
            _eq((self.key, self.arity), (other.key, other.arity))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        if self.__hash is None:
            self.__hash = hash((self.key, self.arity))
        return self.__hash

    def __repr__(self):
        return repr(self.key) + '/' + str(self.arity)

# Blub blub blub
class ImmutableDict(dict):
    """A subclass of Python's built-in `dict` that overrides methods that could mutate the
    dictionary, causing them to raise `TypeError('Immutable')` if called.

    Implements the `__hash__` method, allowing [ImmutableDict][preserves.values.ImmutableDict]
    instances to be used whereever immutable data are permitted; in particular, as keys in
    other dictionaries.

    ```python
    >>> d = ImmutableDict([('a', 1), ('b', 2)])
    >>> d
    {'a': 1, 'b': 2}
    >>> d['c'] = 3
    Traceback (most recent call last):
      ...
    TypeError: Immutable
    >>> del d['b']
    Traceback (most recent call last):
      ...
    TypeError: Immutable

    ```

    """
    def __init__(self, *args, **kwargs):
        if hasattr(self, '__hash'): raise TypeError('Immutable')
        super(ImmutableDict, self).__init__(*args, **kwargs)
        self.__hash = None

    def __delitem__(self, key): raise TypeError('Immutable')
    def __setitem__(self, key, val): raise TypeError('Immutable')
    def clear(self): raise TypeError('Immutable')
    def pop(self, k, d=None): raise TypeError('Immutable')
    def popitem(self): raise TypeError('Immutable')
    def setdefault(self, k, d=None): raise TypeError('Immutable')
    def update(self, e, **f): raise TypeError('Immutable')

    def __hash__(self):
        if self.__hash is None:
            h = 0
            for k in self:
                h = ((h << 5) ^ (hash(k) << 2) ^ hash(self[k])) & sys.maxsize
            self.__hash = h
        return self.__hash

    @staticmethod
    def from_kvs(kvs):
        """Constructs an [ImmutableDict][preserves.values.ImmutableDict] from a sequence of
        alternating keys and values; compare to the
        [ImmutableDict][preserves.values.ImmutableDict] constructor, which takes a sequence of
        key-value pairs.

        ```python
        >>> ImmutableDict.from_kvs(['a', 1, 'b', 2])
        {'a': 1, 'b': 2}
        >>> ImmutableDict.from_kvs(['a', 1, 'b', 2])['c'] = 3
        Traceback (most recent call last):
          ...
        TypeError: Immutable

        ```

        """

        i = iter(kvs)
        result = ImmutableDict()
        result_proxy = super(ImmutableDict, result)
        try:
            while True:
                k = next(i)
                try:
                    v = next(i)
                except StopIteration:
                    raise DecodeError("Missing dictionary value")
                if k in result:
                    raise DecodeError("Duplicate key: " + repr(k))
                result_proxy.__setitem__(k, v)
        except StopIteration:
            pass
        return result

def dict_kvs(d):
    """Generator function yielding a sequence of alternating keys and values from `d`. In some
    sense the inverse of [ImmutableDict.from_kvs][preserves.values.ImmutableDict.from_kvs].

    ```python
    >>> list(dict_kvs({'a': 1, 'b': 2}))
    ['a', 1, 'b', 2]

    ```
    """
    for k in d:
        yield k
        yield d[k]

inf = float('inf')

class Annotated(object):
    """A Preserves `Value` along with a sequence of `Value`s *annotating* it. Compares equal to
    the underlying `Value`, ignoring the annotations. See the [specification document for more
    about annotations](https://preserves.dev/preserves-text.html#annotations).

    ```python
    >>> import preserves
    >>> a = preserves.parse('''
    ... # A comment
    ... [1 2 3]
    ... ''', include_annotations=True)
    >>> a
    @'A comment' (1, 2, 3)
    >>> a.item
    (1, 2, 3)
    >>> a.annotations
    ['A comment']
    >>> a == (1, 2, 3)
    True
    >>> a == preserves.parse('@xyz [1 2 3]', include_annotations=True)
    True
    >>> a[0]
    Traceback (most recent call last):
      ...
    TypeError: 'Annotated' object is not subscriptable
    >>> a.item[0]
    1
    >>> type(a.item[0])
    <class 'preserves.values.Annotated'>
    >>> a.item[0].annotations
    []
    >>> print(preserves.stringify(a))
    @"A comment" [1 2 3]
    >>> print(preserves.stringify(a, include_annotations=False))
    [1 2 3]

    ```

    Attributes:
        item (Value): the underlying annotated `Value`
        annotations (list[Value]): the annotations attached to `self.item`
    """

    def __init__(self, item):
        self.annotations = []
        self.item = item

    def __preserve_write_binary__(self, encoder):
        if encoder.include_annotations:
            for a in self.annotations:
                encoder.buffer.append(0x85)
                encoder.append(a)
        encoder.append(self.item)

    def __preserve_write_text__(self, formatter):
        if formatter.include_annotations:
            for a in self.annotations:
                formatter.chunks.append('@')
                formatter.append(a)
                formatter.chunks.append(' ')
        formatter.append(self.item)

    def strip(self, depth=inf):
        """Calls [strip_annotations][preserves.values.strip_annotations] on `self` and `depth`."""
        return strip_annotations(self, depth)

    def peel(self):
        """Calls [strip_annotations][preserves.values.strip_annotations] on `self` with `depth=1`."""
        return strip_annotations(self, 1)

    def __eq__(self, other):
        return _eq(self.item, _unwrap(other))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.item)

    def __repr__(self):
        return ' '.join(list('@' + repr(a) for a in self.annotations) + [repr(self.item)])

def is_annotated(v):
    """`True` iff `v` is an instance of [Annotated][preserves.values.Annotated]."""
    return isinstance(v, Annotated)

def strip_annotations(v, depth=inf):
    """Exposes `depth` layers of raw structure of
    potentially-[Annotated][preserves.values.Annotated] `Value`s. If `depth==0` or `v` is not
    [Annotated][preserves.values.Annotated], just returns `v`. Otherwise, descends recursively
    into the structure of `v.item`.

    ```python
    >>> import preserves
    >>> a = preserves.parse('@"A comment" [@a 1 @b 2 @c 3]', include_annotations=True)
    >>> is_annotated(a)
    True
    >>> print(preserves.stringify(a))
    @"A comment" [@a 1 @b 2 @c 3]
    >>> print(preserves.stringify(strip_annotations(a)))
    [1 2 3]
    >>> print(preserves.stringify(strip_annotations(a, depth=1)))
    [@a 1 @b 2 @c 3]

    ```
    """

    if depth == 0: return v
    if not is_annotated(v): return v

    next_depth = depth - 1
    def walk(v):
        return strip_annotations(v, next_depth)

    v = v.item
    if isinstance(v, Record):
        return Record(strip_annotations(v.key, depth), tuple(walk(f) for f in v.fields))
    elif isinstance(v, list):
        return tuple(walk(f) for f in v)
    elif isinstance(v, tuple):
        return tuple(walk(f) for f in v)
    elif isinstance(v, set):
        return frozenset(walk(f) for f in v)
    elif isinstance(v, frozenset):
        return frozenset(walk(f) for f in v)
    elif isinstance(v, dict):
        return ImmutableDict.from_kvs(walk(f) for f in dict_kvs(v))
    elif is_annotated(v):
        raise ValueError('Improper annotation structure')
    else:
        return v

def annotate(v, *anns):
    """Wraps `v` in an [Annotated][preserves.values.Annotated] object, if it isn't already
    wrapped, and appends each of the `anns` to the [Annotated][preserves.values.Annotated]'s
    `annotations` sequence. NOTE: Does not recursively ensure that any parts of the argument
    `v` are themselves wrapped in [Annotated][preserves.values.Annotated] objects!

    ```python
    >>> import preserves
    >>> print(preserves.stringify(annotate(123, "A comment", "Another comment")))
    @"A comment" @"Another comment" 123

    ```
    """
    if not is_annotated(v):
        v = Annotated(v)
    for a in anns:
        v.annotations.append(a)
    return v

def _unwrap(x):
    if is_annotated(x):
        return x.item
    else:
        return x

class Embedded:
    """Representation of a Preserves `Embedded` value. For more on the meaning and use of
    embedded values, [see the specification](https://preserves.dev/preserves.html#embeddeds).

    ```python
    >>> import io
    >>> e = Embedded(io.StringIO('some text'))
    >>> e                                        # doctest: +ELLIPSIS
    #:<_io.StringIO object at ...>
    >>> e.embeddedValue                          # doctest: +ELLIPSIS
    <_io.StringIO object at ...>

    ```

    ```python
    >>> import preserves
    >>> print(preserves.stringify(Embedded(None)))
    Traceback (most recent call last):
      ...
    TypeError: Cannot preserves-format: None
    >>> print(preserves.stringify(Embedded(None), format_embedded=lambda x: 'abcdef'))
    #:"abcdef"

    ```

    Attributes:
        embeddedValue:
            any Python value; could be a platform object, could be a representation of a
            Preserves `Value`, could be `None`, could be anything!

    """
    def __init__(self, embeddedValue):
        self.embeddedValue = embeddedValue

    def __eq__(self, other):
        other = _unwrap(other)
        if other.__class__ is self.__class__:
            return self.embeddedValue == other.embeddedValue

    def __hash__(self):
        return hash(self.embeddedValue)

    def __repr__(self):
        return '#:%r' % (self.embeddedValue,)

    def __preserve_write_binary__(self, encoder):
        encoder.buffer.append(0x86)
        encoder.append(encoder.encode_embedded(self.embeddedValue))

    def __preserve_write_text__(self, formatter):
        formatter.chunks.append('#:')
        formatter.append(formatter.format_embedded(self.embeddedValue))
