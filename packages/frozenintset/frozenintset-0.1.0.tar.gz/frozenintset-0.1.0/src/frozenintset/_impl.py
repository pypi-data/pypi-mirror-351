import bisect
import itertools
from collections.abc import (
    Iterable,
    Iterator,
    Set,
)
from typing import NamedTuple, final, Final


def _advance_and_pad_with_none[T](xs: Iterable[T], skip: int = 1) -> Iterator[T | None]:
    it = iter(xs)
    for _ in range(skip):
        next(it, None)
    yield from it
    yield from itertools.repeat(None, skip)


@final
class _Store(NamedTuple):
    store: tuple[tuple[int, int], ...]


@final
class FrozenIntSet(Set[int]):
    """
    A set implementation specialized for Python's big integers (not limited to 64-bit ints).

    Internally keeps a sorted list of non-overlapping ranges with exclusive upper boundary
    as 2-tuples (instead of Python range objects which have a slightly larger footprint).
    """

    __slots__ = ("_store", "_cached_len", "_cached_hash")

    def copy(self):
        """Return a copy of this FrozenIntSet."""
        return FrozenIntSet(self)

    def union(self, *other: "FrozenIntSet") -> "FrozenIntSet":
        """Take the union of this and all other FrozenIntSet instances."""
        if not other:
            return self
        return self | FrozenIntSet.union(*other)

    @staticmethod
    def union_all(rs: Iterable["FrozenIntSet"]) -> "FrozenIntSet":
        """Return a set with all elements from the given sets."""
        it = iter(rs)
        try:
            r = next(it)
        except StopIteration:
            return FrozenIntSet()
        for e in it:
            r = r.union(e)
        return r

    def intersection(self, *other) -> "FrozenIntSet":
        """Return a new set with elements common to the set and all others."""
        if not other:
            return self
        return self & FrozenIntSet.intersection(*other)

    @staticmethod
    def intersection_all(rs: Iterable["FrozenIntSet"]) -> "FrozenIntSet":
        """Return a set with the elements common to all given sets."""
        it = iter(rs)
        try:
            r = next(it)
        except StopIteration:
            return FrozenIntSet()
        for e in it:
            r = r.intersection(e)
        return r

    def difference(self, other) -> "FrozenIntSet":
        """Return a new set with elements in the set that are not in the others."""
        return self - other

    def symmetric_difference(self, other) -> "FrozenIntSet":
        """Return a new set with elements in either the set or other but not both."""
        return self ^ other

    def issubset(self, other) -> bool:
        """Test whether every element in the set is in `other`."""
        return self < other

    def issuperset(self, other) -> bool:
        """Test whether every element in other is in the set."""
        return self > other

    def isdisjoint(self, other) -> bool:
        """Return True if self and other have no elements in common."""
        if not isinstance(other, FrozenIntSet):
            other = FrozenIntSet(other)
        # Efficient two-pointer scan over sorted non-overlapping ranges
        i = j = 0
        xs, ys = self._store, other._store  # pylint: disable=protected-access
        while i < len(xs) and j < len(ys):
            lo0, up0 = xs[i]
            lo1, up1 = ys[j]
            if up0 <= lo1:
                i += 1
            elif up1 <= lo0:
                j += 1
            else:
                return False  # overlap exists
        return True

    @staticmethod
    def _build(iterable: Iterable[int]) -> Iterator[tuple[int, int]]:
        if isinstance(iterable, range):
            yield iterable.start, iterable.stop
        else:
            cp = sorted({*iterable})
            if cp:
                cl = cp[0]
                cu = cp[0]
                for c in _advance_and_pad_with_none(cp):
                    cu += 1
                    if c != cu:
                        yield cl, cu
                        cl = c  # type: ignore[assignment]
                    cu = c  # type: ignore[assignment]

    def __init__(self, iterable: Iterable[int] | _Store | None = None):
        self._cached_len: int | None = None
        self._cached_hash: int | None = None
        store: tuple[tuple[int, int], ...]
        if isinstance(iterable, FrozenIntSet):
            self._cached_len = iterable._cached_len
            self._cached_hash = iterable._cached_hash
            store = iterable._store
        elif isinstance(iterable, _Store):
            # When constructing from _Store, we assume the input is well-formed: sorted, non-overlapping,
            # and non-empty ranges.  This is a trusted internal optimization and is not validated here.
            store = iterable.store
        elif iterable:
            store = tuple(self._build(iterable))
        else:
            store = ()
        self._store: Final[tuple[tuple[int, int], ...]] = store

    def __contains__(self, elem) -> bool:
        # Locate the range that could contain elem
        # noinspection PyTypeChecker
        idx = bisect.bisect_right(self._store, (elem, float("inf")))
        if idx:
            lo, hi = self._store[idx - 1]
            return lo <= elem < hi
        return False

    @property
    def ranges(self) -> Iterable[range]:
        """Return a representation of this FrozenIntSet as a bunch of range objects."""
        for lo, up in self._store:
            yield range(lo, up)

    def __iter__(self) -> Iterator[int]:
        for r in self.ranges:
            yield from r

    def __len__(self) -> int:
        if self._cached_len is None:
            self._cached_len = sum(up - lo for lo, up in self._store)
        return self._cached_len

    def __hash__(self) -> int:
        if self._cached_hash is None:
            self._cached_hash = hash(self._store)
        return self._cached_hash

    def __repr__(self) -> str:
        return "".join([type(self).__name__, "(", repr([rng for rng in self.ranges]), ")"])

    def __str__(self) -> str:
        return repr(self)

    def __bool__(self) -> bool:
        return bool(self._store)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FrozenIntSet):
            return self._store == other._store
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        if isinstance(other, FrozenIntSet):
            return self._store != other._store
        return NotImplemented

    def __and__(self, other: Set[int]) -> "FrozenIntSet":
        if not isinstance(other, FrozenIntSet):
            other = FrozenIntSet(other)
        if not self or not other:
            return FrozenIntSet()

        es = []
        i = j = 0
        xs, ys = self._store, other._store
        while i < len(xs) and j < len(ys):
            lo0, up0 = xs[i]
            lo1, up1 = ys[j]
            # Check for overlap
            lo = max(lo0, lo1)
            up = min(up0, up1)
            if lo < up:
                es.append((lo, up))
            # Advance the one that ends first
            if up0 < up1:
                i += 1
            else:
                j += 1
        return FrozenIntSet(_Store(tuple(es)))

    def __or__(self, other: Set[int]) -> "FrozenIntSet":  # type: ignore[override]
        if not isinstance(other, FrozenIntSet):
            other = FrozenIntSet(other)
        if not self:
            return other
        if not other:
            return self

        es: list[tuple[int, int]] = []
        i = j = 0
        xs, ys = self._store, other._store

        def append_or_merge(r):
            if not es:
                es.append(r)
            else:
                lo0, up0 = es[-1]
                lo1, up1 = r
                if lo1 <= up0:
                    es[-1] = (lo0, max(up0, up1))
                else:
                    es.append(r)

        while i < len(xs) and j < len(ys):
            if xs[i][0] < ys[j][0]:
                append_or_merge(xs[i])
                i += 1
            else:
                append_or_merge(ys[j])
                j += 1
        while i < len(xs):
            append_or_merge(xs[i])
            i += 1
        while j < len(ys):
            append_or_merge(ys[j])
            j += 1

        return FrozenIntSet(_Store(tuple(es)))

    def __sub__(self, other: Set[int]) -> "FrozenIntSet":
        if not isinstance(other, FrozenIntSet):
            other = FrozenIntSet(other)
        if not self:
            return type(self)()
        if not other:
            return self

        es = []
        i = j = 0
        xs, ys = self._store, other._store
        while i < len(xs):
            lo0, up0 = xs[i]
            current_lo = lo0
            while j < len(ys) and ys[j][1] <= current_lo:
                j += 1
            while j < len(ys) and ys[j][0] < up0:
                lo1, up1 = ys[j]
                if lo1 > current_lo:
                    es.append((current_lo, min(lo1, up0)))
                current_lo = max(current_lo, up1)
                if current_lo >= up0:
                    break
                j += 1
            if current_lo < up0:
                es.append((current_lo, up0))
            i += 1
        return FrozenIntSet(_Store(tuple(es)))

    def __xor__(self, other: Set[int]) -> "FrozenIntSet":  # type: ignore[override]
        if not isinstance(other, FrozenIntSet):
            other = FrozenIntSet(other)
        return (self - other) | (other - self)

    def __lt__(self, other: Set[int]) -> bool:
        """True if self is a proper subset of the other."""
        if not isinstance(other, FrozenIntSet):
            other = FrozenIntSet(other)
        if len(self) >= len(other):
            return False
        return all(e in other for e in self)

    def __gt__(self, other: Set[int]) -> bool:
        """True if self is a proper superset of the other."""
        if not isinstance(other, FrozenIntSet):
            other = FrozenIntSet(other)
        if len(self) <= len(other):
            return False
        return all(e in self for e in other)

    def __le__(self, other: Set[int]) -> bool:
        """True if self is a subset of other (inclusive)."""
        if not isinstance(other, FrozenIntSet):
            other = FrozenIntSet(other)
        return all(e in other for e in self)

    def __ge__(self, other: Set[int]) -> bool:
        """True if self is a superset of other (inclusive)."""
        if not isinstance(other, FrozenIntSet):
            other = FrozenIntSet(other)
        return all(e in self for e in other)

    @classmethod
    def from_ranges_unsafe(cls, ranges: Iterable[tuple[int, int]]) -> "FrozenIntSet":
        """
        Construct a FrozenIntSet directly from a sequence of sorted, non-overlapping (lo, hi) tuples,
        where each lo < hi. Assumes input is well-formed and does not perform validation.
        """
        return cls(_Store(tuple(ranges)))

    @classmethod
    def from_ranges(cls, ranges: Iterable[tuple[int, int]]) -> "FrozenIntSet":
        """
        Construct a FrozenIntSet from explicit ranges.
        """
        sorted_ranges = sorted(ranges)
        prev_hi = None
        for lo, hi in sorted_ranges:
            if lo >= hi:
                raise ValueError(f"Invalid range ({lo}, {hi}) — must have lo < hi.")
            if prev_hi is not None and lo < prev_hi:
                raise ValueError("Ranges must be disjoint and sorted.")
            prev_hi = hi
        return cls(_Store(tuple(sorted_ranges)))

    @property
    def min(self) -> int:
        if not self._store:
            raise ValueError("empty FrozenIntSet has no minimum")
        return self._store[0][0]

    @property
    def max(self) -> int:
        if not self._store:
            raise ValueError("empty FrozenIntSet has no maximum")
        return self._store[-1][1] - 1

    def __getitem__(self, index: int | slice) -> int | "FrozenIntSet":
        if isinstance(index, int):
            if index < 0:
                index += len(self)
            if index < 0 or index >= len(self):
                raise IndexError(f"Index {index} out of range")

            for lo, hi in self._store:
                span = hi - lo
                if index < span:
                    return lo + index
                index -= span
            raise RuntimeError("Corrupt IntSet state: index calculation failed")

        if isinstance(index, slice):
            start, stop, step = index.indices(len(self))
            if step == 0:
                raise ValueError("slice step cannot be zero")
            if step == 1:
                # Fast path: contiguous slice
                return type(self)(self[i] for i in range(start, stop))
            else:
                # Slower path for strided slice
                return type(self)(self[i] for i in range(start, stop, step))

        raise TypeError(f"Invalid index type: {type(index)}")
