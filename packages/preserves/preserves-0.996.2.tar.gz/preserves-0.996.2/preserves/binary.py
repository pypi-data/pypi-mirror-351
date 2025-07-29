"""The [preserves.binary][] module implements the [Preserves machine-oriented binary
syntax](https://preserves.dev/preserves-binary.html).

The main entry points are functions [encode][preserves.binary.encode],
[canonicalize][preserves.binary.canonicalize], [decode][preserves.binary.decode], and
[decode_with_annotations][preserves.binary.decode_with_annotations].

```python
>>> encode(Record(Symbol('hi'), []))
b'\\xb4\\xb3\\x02hi\\x84'
>>> decode(b'\\xb4\\xb3\\x02hi\\x84')
#hi()

```

"""

import numbers
import struct

from .values import *
from .error import *
from .compat import basestring_, ord_

class BinaryCodec(object):
    pass

class Decoder(BinaryCodec):
    """Implementation of a decoder for the machine-oriented binary Preserves syntax.

    Args:
        packet (bytes):
            initial contents of the input buffer; may subsequently be extended by calling
            [extend][preserves.binary.Decoder.extend].

        include_annotations (bool):
            if `True`, wrap each value and subvalue in an
            [Annotated][preserves.values.Annotated] object.

        decode_embedded:
            function accepting a `Value` and returning a possibly-decoded form of that value
            suitable for placing into an [Embedded][preserves.values.Embedded] object.

    Normal usage is to supply a buffer, and keep calling [next][preserves.binary.Decoder.next]
    until a [ShortPacket][preserves.error.ShortPacket] exception is raised:

    ```python
    >>> d = Decoder(b'\\xb0\\x01{\\xb1\\x05hello\\x85\\xb3\\x01x\\xb5\\x84')
    >>> d.next()
    123
    >>> d.next()
    'hello'
    >>> d.next()
    ()
    >>> d.next()
    Traceback (most recent call last):
      ...
    preserves.error.ShortPacket: Short packet

    ```

    Alternatively, keep calling [try_next][preserves.binary.Decoder.try_next] until it yields
    `None`, which is not in the domain of Preserves `Value`s:

    ```python
    >>> d = Decoder(b'\\xb0\\x01{\\xb1\\x05hello\\x85\\xb3\\x01x\\xb5\\x84')
    >>> d.try_next()
    123
    >>> d.try_next()
    'hello'
    >>> d.try_next()
    ()
    >>> d.try_next()

    ```

    For convenience, [Decoder][preserves.binary.Decoder] implements the iterator interface,
    backing it with [try_next][preserves.binary.Decoder.try_next], so you can simply iterate
    over all complete values in an input:

    ```python
    >>> d = Decoder(b'\\xb0\\x01{\\xb1\\x05hello\\x85\\xb3\\x01x\\xb5\\x84')
    >>> list(d)
    [123, 'hello', ()]

    ```

    ```python
    >>> for v in Decoder(b'\\xb0\\x01{\\xb1\\x05hello\\x85\\xb3\\x01x\\xb5\\x84'):
    ...     print(repr(v))
    123
    'hello'
    ()

    ```

    Supply `include_annotations=True` to read annotations alongside the annotated values:

    ```python
    >>> d = Decoder(b'\\xb0\\x01{\\xb1\\x05hello\\x85\\xb3\\x01x\\xb5\\x84', include_annotations=True)
    >>> list(d)
    [123, 'hello', @#x ()]

    ```

    If you are incrementally reading from, say, a socket, you can use
    [extend][preserves.binary.Decoder.extend] to add new input as if comes available:

    ```python
    >>> d = Decoder(b'\\xb0\\x01{\\xb1\\x05he')
    >>> d.try_next()
    123
    >>> d.try_next() # returns None because the input is incomplete
    >>> d.extend(b'llo')
    >>> d.try_next()
    'hello'
    >>> d.try_next()

    ```

    Attributes:
        packet (bytes): buffered input waiting to be processed
        index (int): read position within `packet`

    """

    def __init__(self, packet=b'', include_annotations=False, decode_embedded=lambda x: x):
        super(Decoder, self).__init__()
        self.packet = bytearray(packet)
        self.index = 0
        self.include_annotations = include_annotations
        self.decode_embedded = decode_embedded

    def extend(self, data):
        """Appends `data` to the remaining bytes in `self.packet`, trimming already-processed
        bytes from the front of `self.packet` and resetting `self.index` to zero."""
        self.packet[:self.index] = b'' ## apparently amortized O(1) !
        self.packet.extend(data)
        self.index = 0

    def nextbyte(self):
        if self.index >= len(self.packet):
            raise ShortPacket('Short packet')
        self.index = self.index + 1
        return ord_(self.packet[self.index - 1])

    def skipbytes(self, n):
        end = self.index + n
        if end > len(self.packet):
            raise ShortPacket('Short packet')
        self.index = end

    def nextbytes(self, n):
        start = self.index
        self.skipbytes(n)
        end = self.index
        return self.packet[start : end]

    def varint(self):
        v = self.nextbyte()
        if v < 128:
            return v
        else:
            return self.varint() * 128 + (v - 128)

    def peekend(self):
        matched = (self.nextbyte() == 0x84)
        if not matched:
            self.index = self.index - 1
        return matched

    def nextvalues(self):
        result = []
        while not self.peekend():
            result.append(self.next())
        return result

    def nextint(self, n):
        if n == 0: return 0
        acc = self.nextbyte()
        if acc & 0x80: acc = acc - 256
        for _i in range(n - 1):
            acc = (acc << 8) | self.nextbyte()
        return acc

    def wrap(self, v):
        return Annotated(v) if self.include_annotations else v

    def unshift_annotation(self, a, v):
        if self.include_annotations:
            v.annotations.insert(0, a)
        return v

    def skip_value(self):
        """Skips the next complete `Value` from the internal buffer, returning None, and raising
        [ShortPacket][preserves.error.ShortPacket] if too few bytes are available, or
        [DecodeError][preserves.error.DecodeError] if the input is invalid somehow."""
        while True:
            tag = self.nextbyte()
            if tag == 0x80 or tag == 0x81: return
            if tag == 0x81: return
            if tag == 0x84: raise DecodeError('Unexpected end-of-stream marker')
            if tag == 0x85:
                self.skip_value()
                continue
            if tag == 0x86:
                continue
            if tag == 0x87 or tag == 0xb0 or tag == 0xb1 or tag == 0xb2 or tag == 0xb3:
                self.skipbytes(self.varint())
                return
            if tag == 0xb4 or tag == 0xb5 or tag == 0xb6 or tag == 0xb7:
                while not self.peekend():
                    self.skip_value()
                return
            raise DecodeError('Invalid tag: ' + hex(tag))

    def try_skip_value(self):
        """Like [skip_value][preserves.binary.Decoder.skip_value], but returns `True` instead of `None`,
        and returns `False` instead of raising [ShortPacket][preserves.error.ShortPacket]."""
        start = self.index
        try:
            self.skip_value()
            return True
        except ShortPacket:
            self.index = start
            return False

    def complete_value_available(self):
        """Like [try_skip_value][preserves.binary.Decoder.try_skip_value], but never advances
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
        tag = self.nextbyte()
        if tag == 0x80: return self.wrap(False)
        if tag == 0x81: return self.wrap(True)
        if tag == 0x84: raise DecodeError('Unexpected end-of-stream marker')
        if tag == 0x85:
            a = self.next()
            v = self.next()
            return self.unshift_annotation(a, v)
        if tag == 0x86:
            if self.decode_embedded is None:
                raise DecodeError('No decode_embedded function supplied')
            return self.wrap(Embedded(self.decode_embedded(self.next())))
        if tag == 0x87:
            count = self.nextbyte()
            if count == 8: return self.wrap(struct.unpack('>d', self.nextbytes(8))[0])
            raise DecodeError('Invalid IEEE754 size')
        if tag == 0xb0: return self.wrap(self.nextint(self.varint()))
        if tag == 0xb1: return self.wrap(self.nextbytes(self.varint()).decode('utf-8'))
        if tag == 0xb2: return self.wrap(self.nextbytes(self.varint()))
        if tag == 0xb3: return self.wrap(Symbol(self.nextbytes(self.varint()).decode('utf-8')))
        if tag == 0xb4:
            vs = self.nextvalues()
            if not vs: raise DecodeError('Too few elements in encoded record')
            return self.wrap(Record(vs[0], vs[1:]))
        if tag == 0xb5: return self.wrap(tuple(self.nextvalues()))
        if tag == 0xb6:
            vs = self.nextvalues()
            s = frozenset(vs)
            if len(s) != len(vs): raise DecodeError('Duplicate value')
            return self.wrap(s)
        if tag == 0xb7: return self.wrap(ImmutableDict.from_kvs(self.nextvalues()))
        raise DecodeError('Invalid tag: ' + hex(tag))

    def try_next(self):
        """Like [next][preserves.binary.Decoder.next], but returns `None` instead of raising
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

def decode(bs, **kwargs):
    """Yields the first complete encoded value from `bs`, passing `kwargs` through to the
    [Decoder][preserves.binary.Decoder] constructor. Raises exceptions as per
    [next][preserves.binary.Decoder.next].

    Args:
        bs (bytes): encoded data to decode

    """
    return Decoder(packet=bs, **kwargs).next()

def decode_with_annotations(bs, **kwargs):
    """Like [decode][preserves.binary.decode], but supplying `include_annotations=True` to the
    [Decoder][preserves.binary.Decoder] constructor."""
    return Decoder(packet=bs, include_annotations=True, **kwargs).next()

class Encoder(BinaryCodec):
    """Implementation of an encoder for the machine-oriented binary Preserves syntax.

    ```python
    >>> e = Encoder()
    >>> e.append(123)
    >>> e.append('hello')
    >>> e.append(annotate([], Symbol('x')))
    >>> e.contents()
    b'\\xb0\\x01{\\xb1\\x05hello\\x85\\xb3\\x01x\\xb5\\x84'

    ```

    Args:
        encode_embedded:
            function accepting an [Embedded][preserves.values.Embedded].embeddedValue and
            returning a `Value` for serialization.

        canonicalize (bool):
            if `True`, ensures the serialized data are in [canonical
            form](https://preserves.dev/canonical-binary.html). This is slightly more work than
            producing potentially-non-canonical output.

        include_annotations (bool | None):
            if `None`, includes annotations in the output only when `canonicalize` is `False`,
            because [canonical serialization of values demands omission of
            annotations](https://preserves.dev/canonical-binary.html). If explicitly `True` or
            `False`, however, annotations will be included resp. excluded no matter the
            `canonicalize` setting. This can be used to get canonical ordering
            (`canonicalize=True`) *and* annotations (`include_annotations=True`).

    Attributes:
        buffer (bytearray): accumulator for the output of the encoder

    """
    def __init__(self,
                 encode_embedded=lambda x: x,
                 canonicalize=False,
                 include_annotations=None):
        super(Encoder, self).__init__()
        self.buffer = bytearray()
        self._encode_embedded = encode_embedded
        self._canonicalize = canonicalize
        if include_annotations is None:
            self.include_annotations = not self._canonicalize
        else:
            self.include_annotations = include_annotations

    def reset(self):
        """Clears `self.buffer` to a fresh empty `bytearray`."""
        self.buffer = bytearray()

    def encode_embedded(self, v):
        if self._encode_embedded is None:
            raise EncodeError('No encode_embedded function supplied')
        return self._encode_embedded(v)

    def contents(self):
        """Returns a `bytes` constructed from the contents of `self.buffer`."""
        return bytes(self.buffer)

    def varint(self, v):
        if v < 128:
            self.buffer.append(v)
        else:
            self.buffer.append((v % 128) + 128)
            self.varint(v // 128)

    def encodeint(self, v):
        self.buffer.append(0xb0)
        if v == 0:
            bytecount = 0
        else:
            bitcount = (~v if v < 0 else v).bit_length() + 1
            bytecount = (bitcount + 7) // 8
        self.varint(bytecount)
        def enc(n,x):
            if n > 0:
                enc(n-1, x >> 8)
                self.buffer.append(x & 255)
        enc(bytecount, v)

    def encodevalues(self, tag, items):
        self.buffer.append(tag)
        for i in items: self.append(i)
        self.buffer.append(0x84)

    def encodebytes(self, tag, bs):
        self.buffer.append(tag)
        self.varint(len(bs))
        self.buffer.extend(bs)

    def encodeset(self, v):
        if not self._canonicalize:
            self.encodevalues(0xb6, v)
        else:
            c = Canonicalizer(self._encode_embedded, self.include_annotations)
            for i in v: c.entry([i])
            c.emit_entries(self, 0xb6)

    def encodedict(self, v):
        if not self._canonicalize:
            self.encodevalues(0xb7, list(dict_kvs(v)))
        else:
            c = Canonicalizer(self._encode_embedded, self.include_annotations)
            for (kk, vv) in v.items(): c.entry([kk, vv])
            c.emit_entries(self, 0xb7)

    def append(self, v):
        """Extend `self.buffer` with an encoding of `v`."""
        v = preserve(v)
        if hasattr(v, '__preserve_write_binary__'):
            v.__preserve_write_binary__(self)
        elif v is False:
            self.buffer.append(0x80)
        elif v is True:
            self.buffer.append(0x81)
        elif isinstance(v, float):
            self.buffer.append(0x87)
            self.buffer.append(8)
            self.buffer.extend(struct.pack('>d', v))
        elif isinstance(v, numbers.Number):
            self.encodeint(v)
        elif isinstance(v, bytes):
            self.encodebytes(0xb2, v)
        elif isinstance(v, basestring_):
            self.encodebytes(0xb1, v.encode('utf-8'))
        elif isinstance(v, list):
            self.encodevalues(0xb5, v)
        elif isinstance(v, tuple):
            self.encodevalues(0xb5, v)
        elif isinstance(v, set):
            self.encodeset(v)
        elif isinstance(v, frozenset):
            self.encodeset(v)
        elif isinstance(v, dict):
            self.encodedict(v)
        else:
            try:
                i = iter(v)
            except TypeError:
                i = None
            if i is None:
                self.cannot_encode(v)
            else:
                self.encodevalues(0xb5, i)

    def cannot_encode(self, v):
        raise TypeError('Cannot preserves-encode: ' + repr(v))

class Canonicalizer:
    def __init__(self, encode_embedded, include_annotations):
        self.encoder = Encoder(encode_embedded, canonicalize=True, include_annotations=include_annotations)
        self.entries = []

    def entry(self, pieces):
        for piece in pieces: self.encoder.append(piece)
        entry = self.encoder.contents()
        self.encoder.reset()
        self.entries.append(entry)

    def emit_entries(self, outer_encoder, tag):
        outer_encoder.buffer.append(tag)
        for e in sorted(self.entries): outer_encoder.buffer.extend(e)
        outer_encoder.buffer.append(0x84)

def encode(v, **kwargs):
    """Encode a single `Value` `v` to a byte string. Any supplied `kwargs` are passed on to the
    underlying [Encoder][preserves.binary.Encoder] constructor."""
    e = Encoder(**kwargs)
    e.append(v)
    return e.contents()

def canonicalize(v, **kwargs):
    """As [encode][preserves.binary.encode], but sets `canonicalize=True` in the
    [Encoder][preserves.binary.Encoder] constructor.

    """
    return encode(v, canonicalize=True, **kwargs)
