"""The [preserves.merge][] module exports various utilities for merging `Value`s."""

from .values import ImmutableDict, dict_kvs, Embedded, Record

def merge_embedded_id(a, b):
    return a if a is b else None

def merge(v0, *vs, merge_embedded=None):
    """Repeatedly merges `v0` with each element in `vs` using [merge2][preserves.merge.merge2],
    returning the final result. The `merge_embedded` parameter is passed on to merge2."""
    v = v0
    for vN in vs:
        v = merge2(v, vN, merge_embedded=merge_embedded)
    return v

def _die():
    raise ValueError('Cannot merge items')

def merge_seq(aa, bb, merge_embedded=None):
    if len(aa) != len(bb): _die()
    return [merge2(a, b, merge_embedded=merge_embedded) for (a, b) in zip(aa, bb)]

def merge2(a, b, merge_embedded=None):
    """Merges `a` and `b`, returning the result. Raises `ValueError` if, during the merge, a
    pair of incompatible values is discovered.

    If `a` and `b` are [Embedded][preserves.values.Embedded] objects, their `embeddedValue`s
    are merged using `merge_embedded`, and the result is again wrapped in an
    [Embedded][preserves.values.Embedded] object.

    ```python
    >>> merge2(123, 234)
    Traceback (most recent call last):
      ...
    ValueError: Cannot merge items
    >>> merge2(123, 123)
    123
    >>> merge2('hi', 0)
    Traceback (most recent call last):
      ...
    ValueError: Cannot merge items
    >>> merge2([1, 2], [1, 2])
    [1, 2]
    >>> merge2([1, 2], [1, 3])
    Traceback (most recent call last):
      ...
    ValueError: Cannot merge items
    >>> merge2({'a': 1, 'b': 2}, {'a': 1, 'c': 3})
    {'a': 1, 'b': 2, 'c': 3}
    >>> merge2({'a': 1, 'b': 2}, {'a': 10, 'c': 3})
    Traceback (most recent call last):
      ...
    ValueError: Cannot merge items
    >>> merge2(Record('a', [1, {'x': 2}]), Record('a', [1, {'y': 3}]))
    'a'(1, {'x': 2, 'y': 3})

    ```

    """
    if a == b:
        return a
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return merge_seq(a, b)
    if isinstance(a, (set, frozenset)) and isinstance(b, (set, frozenset)):
        _die()
    if isinstance(a, dict) and isinstance(b, dict):
        r = {}
        for (ak, av) in a.items():
            bv = b.get(ak, None)
            r[ak] = av if bv is None else merge2(av, bv, merge_embedded=merge_embedded)
        for (bk, bv) in b.items():
            if bk not in r:
                r[bk] = bv
        return r
    if isinstance(a, Record) and isinstance(b, Record):
        return Record(merge2(a.key, b.key, merge_embedded=merge_embedded),
                      merge_seq(a.fields, b.fields, merge_embedded=merge_embedded))
    if isinstance(a, Embedded) and isinstance(b, Embedded):
        m = (merge_embedded or merge_embedded_id)(a.embeddedValue, b.embeddedValue)
        if m is None: _die()
        return Embedded(m)
    _die()
