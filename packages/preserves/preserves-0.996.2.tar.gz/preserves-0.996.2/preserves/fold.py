"""The [preserves.fold][] module exports various utilities for traversing compound `Value`s."""

from .values import ImmutableDict, dict_kvs, Embedded, Record

def map_embeddeds(f, v):
    """Returns an [equivalent][preserves.compare.eq] copy of `v`, except where each contained
    [Embedded][preserves.values.Embedded] value is replaced by `f` applied to the Embedded's
    `embeddedValue` attribute.

    ```python
    >>> map_embeddeds(lambda w: Embedded(f'w={w}'), ['a', Embedded(123), {'z': 6.0}])
    ('a', #:'w=123', {'z': 6.0})

    ```
    """
    def walk(v):
        if isinstance(v, Embedded):
            return f(v.embeddedValue)
        elif isinstance(v, (list, tuple)):
            return tuple(walk(w) for w in v)
        elif isinstance(v, (set, frozenset)):
            return frozenset(walk(w) for w in v)
        elif isinstance(v, dict):
            return ImmutableDict.from_kvs(walk(w) for w in dict_kvs(v))
        elif isinstance(v, Record):
            return Record(walk(v.key), walk(v.fields))
        else:
            return v
    return walk(v)
