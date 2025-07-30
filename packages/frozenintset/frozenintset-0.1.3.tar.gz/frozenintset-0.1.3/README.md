# frozenintset

**FrozenIntSet** is an immutable, memory-efficient set of integers.
It fully conforms to `collections.abc.Set[int]` and stores values as a sorted list of non-overlapping ranges.


```python
from frozenintset import FrozenIntSet

s = FrozenIntSet({-5, -4, -3, -2, 4, 9, 10, 20, 21, 22})
```

Why `frozenintset`?

✅ Immutable and hashable (usable as dict keys or cache keys)

✅ Efficient for both dense and sparse integer sets

✅ Fast membership testing, iteration, slicing, and set operations

✅ Supports arbitrary-size integers (no 64-bit limit)

## Alternatives

<dl>
<dt><a href="https://pypi.org/project/intset/">intset</a></dt>
<dl>A highly optimized, trie-backed implementation.<br>
⚠️ Limited to 64-bit unsigned integers only.</dl>

<dt><a href="https://pypi.org/project/rangeset/">rangeset</a></dt>
<dl>Supports open and unbounded ranges and arbitrary types.
More general, but frozenintset is faster for plain integers.</dl>
</dl>