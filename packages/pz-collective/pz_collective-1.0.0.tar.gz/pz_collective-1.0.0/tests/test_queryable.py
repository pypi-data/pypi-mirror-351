import pytest
from pz_collective import Collection
from pz_collective import Queryable

def test_where_and_select():
    c = Collection(1, 2, 3, 4, 5)
    q = Queryable(c).Where(lambda x: x % 2 == 0).Select(lambda x: x * 10)
    assert q.ToCollection().ToList() == [20, 40]

def test_limit_and_count():
    c = Collection('a', 'b', 'c', 'd')
    q = Queryable(c).Limit(2)
    assert q.Count() == 2

def test_reverse_and_get():
    c = Collection(1, 2, 3)
    q = Queryable(c).Reverse()
    assert q.Get(0) == 3

def test_distinct():
    c = Collection(1, 1, 2, 3, 3)
    q = Queryable(c).Distinct()
    assert sorted(q.ToCollection().ToList()) == [1, 2, 3]
