import pytest

from frozenintset import FrozenIntSet

def test_union_1():
    x0 = FrozenIntSet([1, 2, 3])
    x1 = FrozenIntSet([3, 4, 5])
    x2 = FrozenIntSet.union(x0, x1)
    assert x2 == FrozenIntSet([1, 2, 3, 4, 5])


def test_union_2():
    x0 = FrozenIntSet([1, 2, 3])
    x1 = FrozenIntSet([2, 3, 4])
    x2 = FrozenIntSet.union(x0, x1)
    assert x2 == FrozenIntSet([1, 2, 3, 4])


def test_union_3():
    x0 = FrozenIntSet([1, 2])
    x1 = FrozenIntSet([3, 4])
    x2 = FrozenIntSet.union(x0, x1)
    assert x2 == FrozenIntSet([1, 2, 3, 4])


def test_union_4():
    x0 = FrozenIntSet([1, 2])
    x1 = FrozenIntSet([4, 5])
    x2 = FrozenIntSet.union(x0, x1)
    assert x2 == FrozenIntSet([1, 2, 4, 5])


def test_intersection_1():
    x0 = FrozenIntSet([1, 2, 3])
    x1 = FrozenIntSet([3, 4, 5])
    x2 = FrozenIntSet.intersection(x0, x1)
    assert x2 == FrozenIntSet([3])


def test_intersection_2():
    x0 = FrozenIntSet([1, 2, 3])
    x1 = FrozenIntSet([2, 3, 4])
    x2 = FrozenIntSet.intersection(x0, x1)
    assert x2 == FrozenIntSet([2, 3])


def test_intersection_3():
    x0 = FrozenIntSet([1, 2])
    x1 = FrozenIntSet([3, 4])
    x2 = FrozenIntSet.intersection(x0, x1)
    assert x2 == FrozenIntSet()


def test_intersection_4():
    x0 = FrozenIntSet([1, 2])
    x1 = FrozenIntSet([4, 5])
    x2 = FrozenIntSet.intersection(x0, x1)
    assert x2 == FrozenIntSet()


def test_intersection_5():
    x0 = FrozenIntSet(range(0, 20))
    x1 = FrozenIntSet([2, 3, 4, 6, 7, 9, 12, 18, 19, 20, 21])
    x2 = FrozenIntSet.intersection(x0, x1)
    assert x2 == FrozenIntSet([2, 3, 4, 6, 7, 9, 12, 18, 19])
    x2 = FrozenIntSet.intersection(x1, x0)
    assert x2 == FrozenIntSet([2, 3, 4, 6, 7, 9, 12, 18, 19])


def test_intersection_6():
    x0 = FrozenIntSet(range(0, 20))
    x1 = FrozenIntSet([2, 3, 4, 6, 7, 9, 12, 18, 19, 20, 21])
    x2 = FrozenIntSet.intersection(x0, x1)
    assert x2 == FrozenIntSet([2, 3, 4, 6, 7, 9, 12, 18, 19])
    x2 = FrozenIntSet.intersection(x1, x0)
    assert x2 == FrozenIntSet([2, 3, 4, 6, 7, 9, 12, 18, 19])


def test_intersection_7():
    x0 = FrozenIntSet(range(0, 3))
    x1 = FrozenIntSet(range(7, 10))
    x2 = FrozenIntSet.intersection(x0, x1)
    assert x2 == FrozenIntSet()


def test_union_all():
    x0 = FrozenIntSet(range(0, 5))
    x1 = FrozenIntSet(range(10, 15))
    x2 = FrozenIntSet(range(3, 12))
    assert FrozenIntSet.union_all([x0, x1, x2]) == FrozenIntSet(range(0, 15))

    rs = FrozenIntSet.union_all(
        [
            FrozenIntSet([1, 2, 3]),
            FrozenIntSet([1, 3, 5]),
            FrozenIntSet([3, 4, 7]),
        ]
    )
    assert rs == FrozenIntSet({1, 2, 3, 4, 5, 7})

    assert FrozenIntSet() == FrozenIntSet.union_all([])


def test_intersection_all_empty():
    assert FrozenIntSet() == FrozenIntSet.intersection_all([])


def test_intersection_all_1():
    x0 = FrozenIntSet(range(8, 11))
    x1 = FrozenIntSet(range(10, 15))
    x2 = FrozenIntSet(range(3, 12))
    assert FrozenIntSet.intersection_all([x0, x1, x2]) == FrozenIntSet([10])


def test_intersection_all_2():
    x0 = FrozenIntSet(range(8, 11))
    x1 = FrozenIntSet(range(10, 15))
    x2 = FrozenIntSet(range(3, 12))
    x3 = FrozenIntSet(range(20, 22))
    assert FrozenIntSet.intersection_all([x0, x1, x2, x3]) == FrozenIntSet()


def test_range_dates():
    FrozenIntSet()


def test_copy():
    x = FrozenIntSet(range(9, 27))
    y = x.copy()
    assert x == y


def test_contains():
    assert 1 in FrozenIntSet(range(1, 10))
    assert 0 not in FrozenIntSet(range(1, 10))
    assert 17 in FrozenIntSet([1, 2, 3, 10, 11, 12, 17, 18, 19, 20, 21, 22, 27, 28, 29])


def test_minus():
    assert (FrozenIntSet() - FrozenIntSet(range(1, 10))) == FrozenIntSet()
    assert FrozenIntSet([1, 2, 3, 4, 8, 9]) - FrozenIntSet([2, 3, 4]) == FrozenIntSet([1, 8, 9])


def test_empty():
    rs = FrozenIntSet()
    assert len(rs) == 0
    assert 1 not in rs
    assert rs.isdisjoint(FrozenIntSet([1]))


def test_singleton():
    rs = FrozenIntSet([5])
    assert len(rs) == 1
    assert 5 in rs
    assert 4 not in rs
    assert 6 not in rs


def test_contiguous():
    rs = FrozenIntSet(range(10, 15))
    assert len(rs) == 5
    assert all(i in rs for i in range(10, 15))
    assert 9 not in rs
    assert 15 not in rs


def test_disjoint():
    rs = FrozenIntSet([1, 2, 3, 10, 11, 12])
    assert len(rs) == 6
    assert set(rs) == {1, 2, 3, 10, 11, 12}
    assert FrozenIntSet([1, 2]) < rs


def test_equality_and_hash():
    a = FrozenIntSet([1, 2, 3, 10])
    b = FrozenIntSet([1, 2, 3, 10])
    c = FrozenIntSet([1, 2, 10])
    assert a == b
    assert hash(a) == hash(b)
    assert a != c


def test_union():
    a = FrozenIntSet([1, 2, 3])
    b = FrozenIntSet([3, 4, 5])
    u = a | b
    assert set(u) == {1, 2, 3, 4, 5}


def test_intersection():
    a = FrozenIntSet([1, 2, 3, 4])
    b = FrozenIntSet([3, 4, 5])
    i = a & b
    assert set(i) == {3, 4}


def test_difference():
    a = FrozenIntSet([1, 2, 3, 4, 5])
    b = FrozenIntSet([2, 3])
    d = a - b
    assert set(d) == {1, 4, 5}


def test_symmetric_difference():
    a = FrozenIntSet([1, 2, 3])
    b = FrozenIntSet([3, 4])
    x = a ^ b
    assert set(x) == {1, 2, 4}


def test_from_ranges():
    rs = FrozenIntSet.from_ranges([(1, 4), (10, 15)])
    assert set(rs) == set(range(1, 4)) | set(range(10, 15))


@pytest.mark.parametrize(
    "bad_input",
    [
        [(5, 5)],  # empty range
        [(5, 4)],  # reversed range
        [(1, 3), (2, 5)],  # overlapping ranges
    ],
)
def test_from_ranges_invalid(bad_input):
    with pytest.raises(ValueError):
        FrozenIntSet.from_ranges(bad_input)
