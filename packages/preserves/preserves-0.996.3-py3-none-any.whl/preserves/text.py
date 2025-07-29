"""The [preserves.text][] module implements the [Preserves human-readable text
syntax](https://preserves.dev/preserves-text.html).

The main entry points are functions [stringify][preserves.text.stringify],
[parse][preserves.text.parse], and
[parse_with_annotations][preserves.text.parse_with_annotations].

```python
>>> stringify(Record(Symbol('hi'), [1, [2, 3]]))
'<hi 1 [2 3]>'
>>> parse('<hi 1 [2 3]>')
#hi(1, (2, 3))

```

"""

import numbers
import struct
import base64
import math

from .values import *
from .error import *
from .compat import basestring_, unichr_
from .binary import Decoder

class TextCodec(object):
    pass

NUMBER_RE = re.compile(r'^([-+]?\d+)((\.\d+([eE][-+]?\d+)?)|([eE][-+]?\d+))?$')

class Parser(TextCodec):
    """Parser for the human-readable Preserves text syntax.

    Args:
        input_buffer (str):
            initial contents of the input buffer; may subsequently be extended by calling
            [extend][preserves.text.Parser.extend].

        include_annotations (bool):
            if `True`, wrap each value and subvalue in an
            [Annotated][preserves.values.Annotated] object.

        parse_embedded:
            function accepting a `Value` and returning a possibly-decoded form of that value
            suitable for placing into an [Embedded][preserves.values.Embedded] object.

    Normal usage is to supply input text, and keep calling [next][preserves.text.Parser.next]
    until a [ShortPacket][preserves.error.ShortPacket] exception is raised:

    ```python
    >>> d = Parser('123 "hello" @x []')
    >>> d.next()
    123
    >>> d.next()
    'hello'
    >>> d.next()
    ()
    >>> d.next()
    Traceback (most recent call last):
      ...
    preserves.error.ShortPacket: Short input buffer

    ```

    Alternatively, keep calling [try_next][preserves.text.Parser.try_next] until it yields
    `None`, which is not in the domain of Preserves `Value`s:

    ```python
    >>> d = Parser('123 "hello" @x []')
    >>> d.try_next()
    123
    >>> d.try_next()
    'hello'
    >>> d.try_next()
    ()
    >>> d.try_next()

    ```

    For convenience, [Parser][preserves.text.Parser] implements the iterator interface,
    backing it with [try_next][preserves.text.Parser.try_next], so you can simply iterate
    over all complete values in an input:

    ```python
    >>> d = Parser('123 "hello" @x []')
    >>> list(d)
    [123, 'hello', ()]

    ```

    ```python
    >>> for v in Parser('123 "hello" @x []'):
    ...     print(repr(v))
    123
    'hello'
    ()

    ```

    Supply `include_annotations=True` to read annotations alongside the annotated values:

    ```python
    >>> d = Parser('123 "hello" @x []', include_annotations=True)
    >>> list(d)
    [123, 'hello', @#x ()]

    ```

    If you are incrementally reading from, say, a socket, you can use
    [extend][preserves.text.Parser.extend] to add new input as if comes available:

    ```python
    >>> d = Parser('123 "he')
    >>> d.try_next()
    123
    >>> d.try_next() # returns None because the input is incomplete
    >>> d.extend('llo"')
    >>> d.try_next()
    'hello'
    >>> d.try_next()

    ```

    Attributes:
        input_buffer (str): buffered input waiting to be processed
        index (int): read position within `input_buffer`

    """

    def __init__(self, input_buffer=u'', include_annotations=False, parse_embedded=lambda x: x):
        super(Parser, self).__init__()
        self.input_buffer = input_buffer
        self.index = 0
        self.include_annotations = include_annotations
        self.parse_embedded = parse_embedded

    def extend(self, text):
        """Appends `text` to the remaining contents of `self.input_buffer`, trimming already-processed
        text from the front of `self.input_buffer` and resetting `self.index` to zero."""
        self.input_buffer = self.input_buffer[self.index:] + text
        self.index = 0

    def _atend(self):
        return self.index >= len(self.input_buffer)

    def peek(self):
        if self._atend():
            raise ShortPacket('Short input buffer')
        return self.input_buffer[self.index]

    def skip(self):
        self.index = self.index + 1

    def nextchar(self):
        c = self.peek()
        self.skip()
        return c

    def skip_whitespace(self, skip_commas = False):
        while not self._atend():
            c = self.peek()
            if not (c.isspace() or (skip_commas and c == ',')):
                break
            self.skip()

    def comment_line(self):
        s = []
        while True:
            c = self.nextchar()
            if c == '\r' or c == '\n':
                return self.wrap(u''.join(s))
            s.append(c)

    def read_stringlike(self, terminator, hexescape, hexescaper):
        acc = []
        while True:
            c = self.nextchar()
            if c == terminator:
                return u''.join(acc)
            if c == '\\':
                c = self.nextchar()
                if c == hexescape: hexescaper(acc)
                elif c == terminator or c == '\\' or c == '/': acc.append(c)
                elif c == 'b': acc.append(u'\x08')
                elif c == 'f': acc.append(u'\x0c')
                elif c == 'n': acc.append(u'\x0a')
                elif c == 'r': acc.append(u'\x0d')
                elif c == 't': acc.append(u'\x09')
                else: raise DecodeError('Invalid escape code')
            else:
                acc.append(c)

    def hexnum(self, count):
        v = 0
        for i in range(count):
            c = self.nextchar().lower()
            if c >= '0' and c <= '9':
                v = v << 4 | (ord(c) - ord('0'))
            elif c >= 'a' and c <= 'f':
                v = v << 4 | (ord(c) - ord('a') + 10)
            else:
                raise DecodeError('Bad hex escape')
        return v

    def read_string(self, delimiter):
        def u16_escape(acc):
            n1 = self.hexnum(4)
            if n1 >= 0xd800 and n1 <= 0xdfff:
                if n1 >= 0xdc00:
                    raise DecodeError('Bad first half of surrogate pair')
                ok = True
                ok = ok and self.nextchar() == '\\'
                ok = ok and self.nextchar() == 'u'
                if not ok:
                    raise DecodeError('Missing second half of surrogate pair')
                n2 = self.hexnum(4)
                if n2 >= 0xdc00 and n2 <= 0xdfff:
                    n = ((n1 - 0xd800) << 10) + (n2 - 0xdc00) + 0x10000
                    acc.append(unichr_(n))
                else:
                    raise DecodeError('Bad second half of surrogate pair')
            else:
                acc.append(unichr_(n1))
        return self.read_stringlike(delimiter, 'u', u16_escape)

    def read_literal_binary(self):
        s = self.read_stringlike('"', 'x', lambda acc: acc.append(unichr_(self.hexnum(2))))
        return s.encode('latin-1')

    def read_hex_binary(self):
        acc = bytearray()
        while True:
            self.skip_whitespace()
            if self.peek() == '"':
                self.skip()
                return bytes(acc)
            acc.append(self.hexnum(2))

    def read_base64_binary(self):
        acc = []
        while True:
            self.skip_whitespace()
            c = self.nextchar()
            if c == ']':
                acc.append(u'====')
                return base64.b64decode(u''.join(acc))
            if c == '-': c = '+'
            if c == '_': c = '/'
            if c == '=': continue
            acc.append(c)

    def read_hex_float(self):
        if self.nextchar() != '"':
            raise DecodeError('Missing open-double-quote in hex-encoded floating-point number')
        bs = self.read_hex_binary()
        if len(bs) != 8:
            raise DecodeError('Incorrect number of bytes in hex-encoded floating-point number')
        return struct.unpack('>d', bs)[0]

    def upto(self, delimiter, skip_commas):
        vs = []
        while True:
            self.skip_whitespace(skip_commas)
            if self.peek() == delimiter:
                self.skip()
                return tuple(vs)
            vs.append(self.next())

    def read_set(self):
        items = self.upto('}', True)
        s = set()
        for i in items:
            if i in s: raise DecodeError('Duplicate value in set: ' + repr(i))
            s.add(i)
        return frozenset(s)

    def read_dictionary(self):
        acc = []
        while True:
            self.skip_whitespace(True)
            if self.peek() == '}':
                self.skip()
                return ImmutableDict.from_kvs(acc)
            acc.append(self.next())
            self.skip_whitespace()
            if self.nextchar() != ':':
                raise DecodeError('Missing expected key/value separator')
            acc.append(self.next())

    def require_delimiter(self, prefix):
        if not self.delimiter_follows():
            raise DecodeError('Delimiter must follow ' + prefix)

    def delimiter_follows(self):
        if self._atend(): return True
        c = self.peek()
        return c.isspace() or c in '(){}[]<>"\';,@#:'

    def read_raw_symbol_or_number(self, acc):
        while not self.delimiter_follows():
            acc.append(self.nextchar())
        acc = u''.join(acc)
        m = NUMBER_RE.match(acc)
        if m:
            if m[2] is None:
                return int(m[1])
            else:
                return float(acc)
        else:
            return Symbol(acc)

    def wrap(self, v):
        return Annotated(v) if self.include_annotations else v

    def unshift_annotation(self, a, v):
        if self.include_annotations:
            # TODO: this will end up O(n^2) for multiple annotations in a row
            v.annotations.insert(0, a)
        return v

    def skip_value(self):
        """Skips the next complete `Value` from the internal buffer, raising
        [ShortPacket][preserves.error.ShortPacket] if too few bytes are available, or
        [DecodeError][preserves.error.DecodeError] if the input is invalid somehow."""
        self.next()

    def try_skip_value(self):
        """Like [skip_value][preserves.text.Parser.skip_value], but returns `True` instead of `None`,
        and returns `False` instead of raising [ShortPacket][preserves.error.ShortPacket]."""
        start = self.index
        try:
            self.skip_value()
            return True
        except ShortPacket:
            self.index = start
            return False

    def complete_value_available(self):
        """Like [try_skip_value][preserves.text.Parser.try_skip_value], but never advances
        the internal read position."""
        start = self.index
        result = self.try_skip_value()
        self.index = start
        return result

    def next(self):
        """Reads the next complete `Value` from the internal buffer, raising
        [ShortPacket][preserves.error.ShortPacket] if too few bytes are available, or
        [DecodeError][preserves.error.DecodeError] if the input is invalid somehow.

        """
        self.skip_whitespace()
        c = self.peek()
        if c == '"':
            self.skip()
            return self.wrap(self.read_string('"'))
        if c == "'":
            self.skip()
            return self.wrap(Symbol(self.read_string("'")))
        if c == '@':
            self.skip()
            return self.unshift_annotation(self.next(), self.next())
        if c == ';':
            raise DecodeError('Semicolon is reserved syntax')
        if c == ':':
            raise DecodeError('Unexpected key/value separator between items')
        if c == '#':
            self.skip()
            c = self.nextchar()
            if c in ' \t': return self.unshift_annotation(self.comment_line(), self.next())
            if c in '\n\r': return self.unshift_annotation('', self.next())
            if c == '!':
                return self.unshift_annotation(
                    Record(Symbol('interpreter'), [self.comment_line()]),
                    self.next())
            if c == 'f': self.require_delimiter('#f'); return self.wrap(False)
            if c == 't': self.require_delimiter('#t'); return self.wrap(True)
            if c == '{': return self.wrap(self.read_set())
            if c == '"': return self.wrap(self.read_literal_binary())
            if c == 'x':
                c = self.nextchar()
                if c == '"': return self.wrap(self.read_hex_binary())
                if c == 'd': return self.wrap(self.read_hex_float())
                raise DecodeError('Invalid #x syntax')
            if c == '[': return self.wrap(self.read_base64_binary())
            if c == ':':
                if self.parse_embedded is None:
                    raise DecodeError('No parse_embedded function supplied')
                return self.wrap(Embedded(self.parse_embedded(self.next())))
            raise DecodeError('Invalid # syntax')
        if c == '<':
            self.skip()
            vs = self.upto('>', False)
            if len(vs) == 0:
                raise DecodeError('Missing record label')
            return self.wrap(Record(vs[0], vs[1:]))
        if c == '[':
            self.skip()
            return self.wrap(self.upto(']', True))
        if c == '{':
            self.skip()
            return self.wrap(self.read_dictionary())
        if c in '>]},':
            raise DecodeError('Unexpected ' + c)
        self.skip()
        return self.wrap(self.read_raw_symbol_or_number([c]))

    def try_next(self):
        """Like [next][preserves.text.Parser.next], but returns `None` instead of raising
        [ShortPacket][preserves.error.ShortPacket]."""
        start = self.index
        try:
            return self.next()
        except ShortPacket:
            self.index = start
            return None

    def __iter__(self):
        return self

    def __next__(self):
        v = self.try_next()
        if v is None:
            raise StopIteration
        return v

def parse(text, **kwargs):
    """Yields the first complete encoded value from `text`, passing `kwargs` through to the
    [Parser][preserves.text.Parser] constructor. Raises exceptions as per
    [next][preserves.text.Parser.next].

    Args:
        text (str): encoded data to decode

    """
    return Parser(input_buffer=text, **kwargs).next()

def parse_with_annotations(bs, **kwargs):
    """Like [parse][preserves.text.parse], but supplying `include_annotations=True` to the
    [Parser][preserves.text.Parser] constructor."""
    return Parser(input_buffer=bs, include_annotations=True, **kwargs).next()

class Formatter(TextCodec):
    """Printer (and indenting pretty-printer) for producing human-readable syntax from
    Preserves `Value`s.

    ```python
    >>> f = Formatter()
    >>> f.append({'a': 1, 'b': 2})
    >>> f.append(Record(Symbol('label'), ['field1', ['field2item1', 'field2item2']]))
    >>> print(f.contents())
    {"a": 1 "b": 2} <label "field1" ["field2item1" "field2item2"]>

    >>> f = Formatter(indent=4)
    >>> f.append({'a': 1, 'b': 2})
    >>> f.append(Record(Symbol('label'), ['field1', ['field2item1', 'field2item2']]))
    >>> print(f.contents())
    {
        "a": 1
        "b": 2
    }
    <label "field1" [
        "field2item1"
        "field2item2"
    ]>

    ```

    Args:
        format_embedded:
            function accepting an [Embedded][preserves.values.Embedded].embeddedValue and
            returning a `Value` for serialization.

        indent (int | None):
            `None` disables indented pretty-printing; otherwise, an `int` specifies indentation
            per nesting-level.

        with_commas (bool):
            `True` causes commas to separate sequence and set items and dictionary entries;
            `False` omits commas.

        trailing_comma (bool):
            `True` causes a comma to be printed *after* the final item or entry in a sequence,
            set or dictionary; `False` omits this trailing comma

        include_annotations (bool):
            `True` causes annotations to be included in the output; `False` causes them to be
            omitted.

    Attributes:
        indent_delta (int): indentation per nesting-level
        chunks (list[str]): fragments of output
    """
    def __init__(self,
                 format_embedded=lambda x: x,
                 indent=None,
                 with_commas=False,
                 trailing_comma=False,
                 include_annotations=True):
        super(Formatter, self).__init__()
        self.indent_delta = 0 if indent is None else indent
        self.indent_distance = 0
        self.nesting = 0
        self.with_commas = with_commas
        self.trailing_comma = trailing_comma
        self.chunks = []
        self._format_embedded = format_embedded
        self.include_annotations = include_annotations

    def format_embedded(self, v):
        if self._format_embedded is None:
            raise EncodeError('No format_embedded function supplied')
        return self._format_embedded(v)

    def contents(self):
        """Returns a `str` constructed from the join of the chunks in `self.chunks`."""
        return u''.join(self.chunks)

    def is_indenting(self):
        """Returns `True` iff this [Formatter][preserves.text.Formatter] is in pretty-printing
        indenting mode."""
        return self.indent_delta > 0

    def write_indent(self):
        if self.is_indenting():
            self.chunks.append('\n' + ' ' * self.indent_distance)

    def write_indent_space(self):
        if self.is_indenting():
            self.write_indent()
        else:
            self.chunks.append(' ')

    def write_stringlike_char(self, c):
        if c == '\\': self.chunks.append('\\\\')
        elif c == '\x08': self.chunks.append('\\b')
        elif c == '\x0c': self.chunks.append('\\f')
        elif c == '\x0a': self.chunks.append('\\n')
        elif c == '\x0d': self.chunks.append('\\r')
        elif c == '\x09': self.chunks.append('\\t')
        else: self.chunks.append(c)

    def write_seq(self, opener, closer, vs, appender):
        vs = list(vs)
        itemcount = len(vs)
        self.chunks.append(opener)
        if itemcount == 0:
            pass
        elif itemcount == 1:
            appender(vs[0])
        else:
            self.indent_distance = self.indent_distance + self.indent_delta
            self.write_indent()
            appender(vs[0])
            for v in vs[1:]:
                if self.with_commas: self.chunks.append(',')
                self.write_indent_space()
                appender(v)
            self.indent_distance = self.indent_distance - self.indent_delta
            if self.trailing_comma: self.chunks.append(',')
            self.write_indent()
        self.chunks.append(closer)

    def append(self, v):
        """Extend `self.chunks` with at least one chunk, together making up the text
        representation of `v`."""
        if self.chunks and self.nesting == 0:
            self.write_indent_space()
        try:
            self.nesting += 1
            self._append(v)
        finally:
            self.nesting -= 1

    def _append(self, v):
        v = preserve(v)
        if hasattr(v, '__preserve_write_text__'):
            v.__preserve_write_text__(self)
        elif v is False:
            self.chunks.append('#f')
        elif v is True:
            self.chunks.append('#t')
        elif isinstance(v, float):
            if math.isnan(v) or math.isinf(v):
                self.chunks.append('#xd"' + struct.pack('>d', v).hex() + '"')
            else:
                self.chunks.append(repr(v))
        elif isinstance(v, numbers.Number):
            self.chunks.append('%d' % (v,))
        elif isinstance(v, bytes):
            self.chunks.append('#[%s]' % (base64.b64encode(v).decode('ascii'),))
        elif isinstance(v, basestring_):
            self.chunks.append('"')
            for c in v:
                if c == '"': self.chunks.append('\\"')
                else: self.write_stringlike_char(c)
            self.chunks.append('"')
        elif isinstance(v, list):
            self.write_seq('[', ']', v, self._append)
        elif isinstance(v, tuple):
            self.write_seq('[', ']', v, self._append)
        elif isinstance(v, set):
            self.write_seq('#{', '}', v, self._append)
        elif isinstance(v, frozenset):
            self.write_seq('#{', '}', v, self._append)
        elif isinstance(v, dict):
            def append_kv(kv):
                self._append(kv[0])
                self.chunks.append(': ')
                self._append(kv[1])
            self.write_seq('{', '}', v.items(), append_kv)
        else:
            try:
                i = iter(v)
            except TypeError:
                i = None
            if i is None:
                self.cannot_format(v)
            else:
                self.write_seq('[', ']', i, self._append)

    def cannot_format(self, v):
        raise TypeError('Cannot preserves-format: ' + repr(v))

def stringify(v, **kwargs):
    """Convert a single `Value` `v` to a string. Any supplied `kwargs` are passed on to the
    underlying [Formatter][preserves.text.Formatter] constructor."""
    e = Formatter(**kwargs)
    e.append(v)
    return e.contents()
