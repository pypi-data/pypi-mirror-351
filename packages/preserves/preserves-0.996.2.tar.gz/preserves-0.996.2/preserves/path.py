"""The [preserves.path][] module implements [Preserves
Path](https://preserves.dev/preserves-path.html).

Preserves Path is roughly analogous to
[XPath](https://www.w3.org/TR/2017/REC-xpath-31-20170321/), but for Preserves values: just as
XPath selects portions of an XML document, a Preserves Path uses *path expressions* to select
portions of a `Value`.

Use [parse][preserves.path.parse] to compile a path expression, and then use the
[exec][preserves.path.exec] method on the result to apply it to a given input:

```python
parse(PATH_EXPRESSION_STRING).exec(PRESERVES_VALUE)
    -> SEQUENCE_OF_PRESERVES_VALUES
```

## Command-line usage

When [preserves.path][] is run as a `__main__` module, `sys.argv[1]` is
[parsed][preserves.path.parse], interpreted as a path expression, and
[run][preserves.path.exec] against [human-readable values][preserves.text] read from standard
input. Each matching result is passed to [stringify][preserves.text.stringify] and printed to
standard output.

## Examples

### Setup: Loading test data

The following examples use `testdata`:

```python
>>> with open('tests/samples.bin', 'rb') as f:
...     testdata = decode_with_annotations(f.read())

```

Recall that `samples.bin` contains a binary-syntax form of the human-readable
[`samples.pr](https://preserves.dev/tests/samples.pr) test data file, intended to exercise most
of the features of Preserves. In particular, the root `Value` in the file has a number of
annotations (for documentation and other purposes).

### Example 1: Selecting string-valued documentation annotations

The path expression `.annotations ^ Documentation . 0 / string` proceeds in five steps:

1. `.annotations` selects each annotation on the root document
2. `^ Documentation` retains only those values (each an annotation of the root) that are `Record`s with label equal to the symbol `Documentation`
3. `. 0` moves into the first child (the first field) of each such `Record`, which in our case is a list of other `Value`s
4. `/` selects all immediate children of these lists
5. `string` retains only those values that are strings

The result of evaluating it on `testdata` is as follows:

```python
>>> selector = parse('.annotations ^ Documentation . 0 / string')
>>> for result in selector.exec(testdata):
...     print(stringify(result))
"Individual test cases may be any of the following record types:"
"In each test, let stripped = strip(annotatedValue),"
"                  encodeBinary(·) produce canonical ordering and no annotations,"
"                  looseEncodeBinary(·) produce any ordering, but with annotations,"
"                  annotatedBinary(·) produce “canonical ordering”, but with annotations,"
"                  decodeBinary(·) include annotations,"
"                  encodeText(·) include annotations,"
"                  decodeText(·) include annotations,"
"and check the following numbered expectations according to the table above:"
"Implementations may vary in their treatment of the difference between expectations"
"21/22 and 31/32, depending on how they wish to treat end-of-stream conditions."
"The idea of canonical-ordering-with-annotations is to encode, say, sets with their elements"
"in sorted order of their canonical annotationless binary encoding, but then actually"
"*serialized* with the annotations present."

```

### Example 2: Selecting tests with Records as their annotatedValues

The path expression `// [.^ [= Test + = NondeterministicTest]] [. 1 rec]` proceeds in three steps:

1. `//` recursively decomposes the input, yielding all direct and indirect descendants of each input value

2. `[.^ [= Test + = NondeterministicTest]]` retains only those inputs (each a descendant of the root) that yield more than zero results when executed against the expression within the brackets:
    1. `.^` selects only labels of values that are `Records`, filtering by type and transforming in a single step
    2. `[= Test + = NondeterministicTest]` again filters by a path expression:
        1. the infix `+` operator takes the *union* of matches of its arguments
        2. the left-hand argument, `= Test` selects values (remember, record labels) equal to the symbol `Test`
        3. the right-hand argument `= NondeterministicTest` selects values equal to `NondeterministicTest`

    The result is thus all `Record`s anywhere inside `testdata` that have either `Test` or `NondeterministicTest` as their labels.

3. `[. 1 rec]` filters these `Record`s by another path expression:
    1. `. 1` selects their second field (fields are numbered from 0)
    2. `rec` retains only values that are `Record`s

Evaluating the expression against `testdata` yields the following:

```python
>>> selector = parse('// [.^ [= Test + = NondeterministicTest]] [. 1 rec]')
>>> for result in selector.exec(testdata):
...     print(stringify(result))
<Test #[tLMHY2FwdHVyZbSzB2Rpc2NhcmSEhA==] <capture <discard>>>
<Test #[tLMHb2JzZXJ2ZbSzBXNwZWFrtLMHZGlzY2FyZIS0swdjYXB0dXJltLMHZGlzY2FyZISEhIQ=] <observe <speak <discard> <capture <discard>>>>>
<Test #[tLWzBnRpdGxlZLMGcGVyc29usAECswV0aGluZ7ABAYSwAWWxCUJsYWNrd2VsbLSzBGRhdGWwAgcdsAECsAEDhLECRHKE] <[titled person 2 thing 1] 101 "Blackwell" <date 1821 2 3> "Dr">>
<Test #[tLMHZGlzY2FyZIQ=] <discard>>
<Test #[tLABB7WEhA==] <7 []>>
<Test #[tLMHZGlzY2FyZLMIc3VycHJpc2WE] <discard surprise>>
<Test #[tLEHYVN0cmluZ7ABA7ABBIQ=] <"aString" 3 4>>
<Test #[tLSzB2Rpc2NhcmSEsAEDsAEEhA==] <<discard> 3 4>>
<Test #[hbMCYXK0swFShbMCYWazAWaE] @ar <R @af f>>
<Test #[tIWzAmFyswFShbMCYWazAWaE] <@ar R @af f>>

```

"""

from . import *
from .schema import load_schema_file, extend
from .values import _unwrap
from .compat import basestring_
from . import compare as preserves_compare
import pathlib
import re

syntax = load_schema_file(pathlib.Path(__file__).parent / 'path.prb').path
"""This value is a Python representation of a [Preserves Schema][preserves.schema] definition
for the Preserves Path expression language. The language is defined in the file
[path.prs](https://preserves.dev/path/path.prs)."""

Selector = syntax.Selector
"""Schema definition for representing a sequence of Preserves Path `Step`s."""

Predicate = syntax.Predicate
"""Schema definition for representing a Preserves Path `Predicate`."""

def parse(s):
    """Parse `s` as a Preserves Path path expression, yielding a
    [Selector][preserves.path.Selector] object. Selectors (and Predicates etc.) have an
    [exec][preserves.path.exec] method defined on them.

    Raises `ValueError` if `s` is not a valid path expression.

    """
    return parse_selector(Parser(s))

def parse_selector(tokens):
    steps = []
    tokens = iter(tokens)
    while True:
        try:
            steps.append(parse_step(tokens))
        except StopIteration:
            return syntax.Selector(steps)

AXIS_VALUES = Symbol('/')
AXIS_DESCENDANTS = Symbol('//')
AXIS_MEMBER = Symbol('.')
AXIS_LABEL = Symbol('.^')
AXIS_KEYS = Symbol('.keys')
AXIS_LENGTH = Symbol('.length')
AXIS_ANNOTATIONS = Symbol('.annotations')
AXIS_EMBEDDED = Symbol('.embedded')

FILTER_NOP = Symbol('*')
FILTER_EQ1 = Symbol('eq')
FILTER_EQ2 = Symbol('=')
FILTER_NE1 = Symbol('ne')
FILTER_NE2 = Symbol('!=')
FILTER_LT = Symbol('lt')
FILTER_LE = Symbol('le')
FILTER_GT = Symbol('gt')
FILTER_GE = Symbol('ge')
FILTER_RE1 = Symbol('re')
FILTER_RE2 = Symbol('=r')
FILTER_LABEL = Symbol('^')

FILTER_BOOL = Symbol('bool')
FILTER_DOUBLE = Symbol('double')
FILTER_INT = Symbol('int')
FILTER_STRING = Symbol('string')
FILTER_BYTES = Symbol('bytes')
FILTER_SYMBOL = Symbol('symbol')
FILTER_REC = Symbol('rec')
FILTER_SEQ = Symbol('seq')
FILTER_SET = Symbol('set')
FILTER_DICT = Symbol('dict')
FILTER_EMBEDDED = Symbol('embedded')

FUNCTION_COUNT = Symbol('count')

TRANSFORM_REAL = Symbol('~real')
TRANSFORM_INT = Symbol('~int')

def parse_step(tokens):
    t = next(tokens)
    if isinstance(t, tuple): return syntax.Step.Filter(syntax.Filter.test(parse_predicate(t)))
    if isinstance(t, Record):
        if t.key == FUNCTION_COUNT: return syntax.Step.Function(syntax.Function(parse_selector(t.fields)))
        raise ValueError('Invalid Preserves path function: ' + repr(t))
    if t == AXIS_VALUES: return syntax.Step.Axis(syntax.Axis.values())
    if t == AXIS_DESCENDANTS: return syntax.Step.Axis(syntax.Axis.descendants())
    if t == AXIS_MEMBER: return syntax.Step.Axis(syntax.Axis.at(next(tokens)))
    if t == AXIS_LABEL: return syntax.Step.Axis(syntax.Axis.label())
    if t == AXIS_KEYS: return syntax.Step.Axis(syntax.Axis.keys())
    if t == AXIS_LENGTH: return syntax.Step.Axis(syntax.Axis.length())
    if t == AXIS_ANNOTATIONS: return syntax.Step.Axis(syntax.Axis.annotations())
    if t == AXIS_EMBEDDED: return syntax.Step.Axis(syntax.Axis.embedded())
    if t == FILTER_NOP: return syntax.Step.Filter(syntax.Filter.nop())
    if t == FILTER_EQ1 or t == FILTER_EQ2: return parse_comparison(tokens, syntax.Comparison.eq())
    if t == FILTER_NE1 or t == FILTER_NE2: return parse_comparison(tokens, syntax.Comparison.ne())
    if t == FILTER_LT: return parse_comparison(tokens, syntax.Comparison.lt())
    if t == FILTER_GT: return parse_comparison(tokens, syntax.Comparison.gt())
    if t == FILTER_LE: return parse_comparison(tokens, syntax.Comparison.le())
    if t == FILTER_GE: return parse_comparison(tokens, syntax.Comparison.ge())
    if t == FILTER_RE1 or t == FILTER_RE2:
        re_val = next(tokens)
        if not isinstance(re_val, str): raise ValueError('Expected string argument to re/=r')
        try:
            re.compile(re_val)
        except:
            raise ValueError('Invalid regular expression')
        return syntax.Step.Filter(syntax.Filter.regex(re_val))
    if t == FILTER_LABEL:
        label_lit = next(tokens)
        return syntax.Step.Filter(syntax.Filter.test(syntax.Predicate.Selector(syntax.Selector([
            syntax.Step.Axis(syntax.Axis.label()),
            syntax.Step.Filter(syntax.Filter.compare(
                syntax.Comparison.eq(),
                label_lit))]))))
    if t == TRANSFORM_REAL: return syntax.Step.Filter(syntax.Filter.real)
    if t == TRANSFORM_INT: return syntax.Step.Filter(syntax.Filter.int)
    if t == FILTER_BOOL: return kind_filter(syntax.ValueKind.Boolean())
    if t == FILTER_DOUBLE: return kind_filter(syntax.ValueKind.Double())
    if t == FILTER_INT: return kind_filter(syntax.ValueKind.SignedInteger())
    if t == FILTER_STRING: return kind_filter(syntax.ValueKind.String())
    if t == FILTER_BYTES: return kind_filter(syntax.ValueKind.ByteString())
    if t == FILTER_SYMBOL: return kind_filter(syntax.ValueKind.Symbol())
    if t == FILTER_REC: return kind_filter(syntax.ValueKind.Record())
    if t == FILTER_SEQ: return kind_filter(syntax.ValueKind.Sequence())
    if t == FILTER_SET: return kind_filter(syntax.ValueKind.Seq())
    if t == FILTER_DICT: return kind_filter(syntax.ValueKind.Dictionary())
    if t == FILTER_EMBEDDED: return kind_filter(syntax.ValueKind.Embedded())
    raise ValueError('Invalid Preserves path step: ' + repr(t))

def kind_filter(value_kind):
    return syntax.Step.Filter(syntax.Filter.kind(value_kind))

def parse_comparison(tokens, op):
    return syntax.Step.Filter(syntax.Filter.compare(op, next(tokens)))

OP_NOT = Symbol('!')
OP_PLUS = Symbol('+')
OP_AND = Symbol('&')

def split_by(tokens, delimiter):
    groups = []
    group = []
    def finish():
        groups.append(group[:])
        group.clear()
    for t in tokens:
        if t == delimiter:
            finish()
        else:
            group.append(t)
    finish()
    return groups

def parse_predicate(tokens):
    tokens = list(tokens)
    union_pieces = split_by(tokens, OP_PLUS)
    intersection_pieces = split_by(tokens, OP_AND)
    if len(union_pieces) > 1 and len(intersection_pieces) > 1:
        raise ValueError('Ambiguous parse: mixed "+" and "&" operators')
    if len(union_pieces) > 1:
        return syntax.Predicate.or_([parse_non_binop(ts) for ts in union_pieces])
    if len(intersection_pieces) > 1:
        return syntax.Predicate.and_([parse_non_binop(ts) for ts in intersection_pieces])
    return parse_non_binop(union_pieces[0])

def parse_non_binop(tokens):
    if tokens[:1] == [OP_NOT]:
        return syntax.Predicate.not_(parse_non_binop(tokens[1:]))
    else:
        return syntax.Predicate.Selector(parse_selector(tokens))

@extend(syntax.Predicate.Selector)
def exec(self, v):
    result = self.value.exec(v)
    return len(tuple(result)) > 0

@extend(syntax.Predicate.not_)
def exec(self, v):
    return not self.pred.exec(v)

@extend(Predicate.or_)
def exec(self, v):
    for p in self.preds:
        if p.exec(v): return True
    return False

@extend(Predicate.and_)
def exec(self, v):
    for p in self.preds:
        if not p.exec(v): return False
    return True

@extend(Selector)
def exec(self, v):
    vs = (v,)
    for step in self.value:
        vs = tuple(w for v in vs for w in step.exec(v))
    return vs

@extend(syntax.Step.Axis)
@extend(syntax.Step.Filter)
@extend(syntax.Step.Function)
def exec(self, v):
    return self.value.exec(v)

def children(value):
    value = _unwrap(preserve(_unwrap(value)))
    if isinstance(value, Record):
        return value.fields
    if isinstance(value, list) or isinstance(value, tuple):
        return tuple(value)
    if isinstance(value, set) or isinstance(value, frozenset):
        return tuple(value)
    if isinstance(value, dict):
        return tuple(value.values())
    return ()

def descendants(value):
    acc = [value]
    i = 0
    while i < len(acc):
        acc.extend(children(acc[i]))
        i = i + 1
    return tuple(acc)

@extend(syntax.Axis.values)
def exec(self, v):
    return children(v)

@extend(syntax.Axis.descendants)
def exec(self, v):
    return descendants(v)

@extend(syntax.Axis.at)
def exec(self, v):
    v = preserve(_unwrap(v))
    if isinstance(v, Symbol):
        v = v.name
    try:
        return (v[self.key],)
    except:
        return ()

@extend(syntax.Axis.label)
def exec(self, v):
    v = preserve(_unwrap(v))
    return (v.key,) if isinstance(v, Record) else ()

@extend(syntax.Axis.keys)
def exec(self, v):
    v = preserve(_unwrap(v))
    if isinstance(v, Symbol):
        return tuple(range(len(v.name)))
    if isinstance(v, basestring_) or \
       isinstance(v, list) or \
       isinstance(v, tuple) or \
       isinstance(v, bytes):
        return tuple(range(len(v)))
    if isinstance(v, Record):
        return tuple(range(len(v.fields)))
    if isinstance(v, dict):
        return tuple(v.keys())
    return ()

@extend(syntax.Axis.length)
def exec(self, v):
    v = preserve(_unwrap(v))
    if isinstance(v, Symbol):
        return (len(v.name),)
    if isinstance(v, basestring_) or \
       isinstance(v, list) or \
       isinstance(v, tuple) or \
       isinstance(v, bytes) or \
       isinstance(v, dict):
        return (len(v),)
    if isinstance(v, Record):
        return (len(v.fields),)
    return (0,)

@extend(syntax.Axis.annotations)
def exec(self, v):
    return tuple(v.annotations) if is_annotated(v) else ()

@extend(syntax.Axis.embedded)
def exec(self, v):
    v = preserve(_unwrap(v))
    return (v.embeddedValue,) if isinstance(v, Embedded) else ()

@extend(syntax.Filter.nop)
def exec(self, v):
    return (v,)

@extend(syntax.Filter.compare)
def exec(self, v):
    v = preserve(_unwrap(v))
    return (v,) if self.op.compare(v, self.literal) else ()

@extend(syntax.Comparison.eq)
def compare(self, lhs, rhs):
    return preserves_compare.eq(lhs, rhs)

@extend(syntax.Comparison.ne)
def compare(self, lhs, rhs):
    return not preserves_compare.eq(lhs, rhs)

@extend(syntax.Comparison.lt)
def compare(self, lhs, rhs):
    return preserves_compare.lt(lhs, rhs)

@extend(syntax.Comparison.ge)
def compare(self, lhs, rhs):
    return not preserves_compare.lt(lhs, rhs)

@extend(syntax.Comparison.gt)
def compare(self, lhs, rhs):
    return not preserves_compare.le(lhs, rhs)

@extend(syntax.Comparison.le)
def compare(self, lhs, rhs):
    return preserves_compare.le(lhs, rhs)

@extend(syntax.Filter.regex)
def exec(self, v):
    r = re.compile(self.regex)
    v = preserve(_unwrap(v))
    if isinstance(v, Symbol):
        return (v,) if r.match(v.name) else ()
    if isinstance(v, basestring_):
        return (v,) if r.match(v) else ()
    return ()

@extend(syntax.Filter.test)
def exec(self, v):
    return (v,) if self.pred.exec(v) else ()

@extend(syntax.Filter.real)
def exec(self, v):
    v = preserve(_unwrap(v))
    if type(v) == float:
        return (v,)
    if type(v) == int:
        return (float(v),)
    return ()

@extend(syntax.Filter.int)
def exec(self, v):
    v = preserve(_unwrap(v))
    if type(v) == float:
        return (int(v),)
    if type(v) == int:
        return (v,)
    return ()

@extend(syntax.Filter.kind)
def exec(self, v):
    v = preserve(_unwrap(v))
    return self.kind.exec(v)

@extend(syntax.ValueKind.Boolean)
def exec(self, v):
    return (v,) if type(v) == bool else ()

@extend(syntax.ValueKind.Double)
def exec(self, v):
    return (v,) if type(v) == float else ()

@extend(syntax.ValueKind.SignedInteger)
def exec(self, v):
    return (v,) if type(v) == int else ()

@extend(syntax.ValueKind.String)
def exec(self, v):
    return (v,) if isinstance(v, basestring_) else ()

@extend(syntax.ValueKind.ByteString)
def exec(self, v):
    return (v,) if isinstance(v, bytes) else ()

@extend(syntax.ValueKind.Symbol)
def exec(self, v):
    return (v,) if isinstance(v, Symbol) else ()

@extend(syntax.ValueKind.Record)
def exec(self, v):
    return (v,) if isinstance(v, Record) else ()

@extend(syntax.ValueKind.Sequence)
def exec(self, v):
    return (v,) if type(v) in [list, tuple] else ()

@extend(syntax.ValueKind.Set)
def exec(self, v):
    return (v,) if type(v) in [set, frozenset] else ()

@extend(syntax.ValueKind.Dictionary)
def exec(self, v):
    return (v,) if isinstance(v, dict) else ()

@extend(syntax.ValueKind.Embedded)
def exec(self, v):
    return (v,) if isinstance(v, Embedded) else ()

@extend(syntax.Function)
def exec(self, v):
    """WARNING: This is not a *function*: it is a *method* on
    [Selector][preserves.path.Selector], [Predicate][preserves.path.Predicate], and so on.

    ```python
    >>> sel = parse('/ [.length gt 1]')
    >>> sel.exec(['', 'a', 'ab', 'abc', 'abcd', 'bcd', 'cd', 'd', ''])
    ('ab', 'abc', 'abcd', 'bcd', 'cd')

    ```

    """
    return (len(self.selector.exec(v)),)

### NOTE WELL: the *LAST* definition of exec in this file is the one that needs the docstring
### attached!

if __name__ == '__main__':
    import sys
    sel = parse(sys.argv[1])
    d = Parser()
    while True:
        chunk = sys.stdin.readline()
        if chunk == '': break
        d.extend(chunk)
        for v in d:
            for w in sel.exec(v):
                print(stringify(w))
