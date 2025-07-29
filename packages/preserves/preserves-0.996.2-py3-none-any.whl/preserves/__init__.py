'''```
import preserves
```

The main package re-exports a subset of the exports of its constituent modules:

- From [preserves.values][]:
    - [Annotated][preserves.values.Annotated]
    - [Embedded][preserves.values.Embedded]
    - [ImmutableDict][preserves.values.ImmutableDict]
    - [Record][preserves.values.Record]
    - [Symbol][preserves.values.Symbol]
    - [annotate][preserves.values.annotate]
    - [is_annotated][preserves.values.is_annotated]
    - [preserve][preserves.values.preserve]
    - [strip_annotations][preserves.values.strip_annotations]

- From [preserves.error][]:
    - [DecodeError][preserves.error.DecodeError]
    - [EncodeError][preserves.error.EncodeError]
    - [ShortPacket][preserves.error.ShortPacket]

- From [preserves.binary][]:
    - [Decoder][preserves.binary.Decoder]
    - [Encoder][preserves.binary.Encoder]
    - [canonicalize][preserves.binary.canonicalize]
    - [decode][preserves.binary.decode]
    - [decode_with_annotations][preserves.binary.decode_with_annotations]
    - [encode][preserves.binary.encode]

- From [preserves.text][]:
    - [Formatter][preserves.text.Formatter]
    - [Parser][preserves.text.Parser]
    - [parse][preserves.text.parse]
    - [parse_with_annotations][preserves.text.parse_with_annotations]
    - [stringify][preserves.text.stringify]

- From [preserves.compare][]:
    - [cmp][preserves.compare.cmp]

- From [preserves.merge][]:
    - [merge][preserves.merge.merge]

It also exports the [compare][preserves.compare] and [fold][preserves.fold] modules themselves,
permitting patterns like

```python
>>> from preserves import *
>>> compare.cmp(123, 234)
-1

```

Finally, it provides a few utility aliases for common tasks:

'''

from .values import Symbol, Record, ImmutableDict, Embedded, preserve

from .values import Annotated, is_annotated, strip_annotations, annotate

from .compare import cmp

from .error import DecodeError, EncodeError, ShortPacket

from .binary import Decoder, Encoder, decode, decode_with_annotations, encode, canonicalize
from .text import Parser, Formatter, parse, parse_with_annotations, stringify

from .merge import merge

from . import fold, compare, schema

loads = parse
'''
This alias for `parse` provides a familiar pythonesque name for converting a string to a Preserves `Value`.
'''

dumps = stringify
'''
This alias for `stringify` provides a familiar pythonesque name for converting a Preserves `Value` to a string.
'''
