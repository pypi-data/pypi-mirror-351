import pytest
from pz_collective import Collection

def test_add_and_count():
    c = Collection()
    c.Add(1).Add(2).Add(3)
    assert c.Count() == 3

def test_remove():
    c = Collection(1, 2, 3)
    c.Remove(2)
    assert c.Count() == 2
    assert not c.Contains(2)

def test_get_and_insert():
    c = Collection('a', 'b', 'c')
    assert c.Get(1) == 'b'
    c.Insert(1, 'x')
    assert c.Get(1) == 'x'

def test_filter_and_map():
    c = Collection(1, 2, 3, 4)
    evens = c.Filter(lambda x: x % 2 == 0)
    assert evens.ToList() == [2, 4]
    doubled = c.Map(lambda x: x * 2)
    assert doubled.ToList() == [2, 4, 6, 8]

def test_distinct():
    c = Collection(1, 1, 2, 2, 3)
    unique = c.Distinct()
    assert sorted(unique.ToList()) == [1, 2, 3]

def test_reverse_and_sort():
    c = Collection(3, 1, 2)
    c.Sort()
    assert c.ToList() == [1, 2, 3]
    c.Reverse()
    assert c.ToList() == [3, 2, 1]

def test_add_and_extend():
    c = Collection()
    c.Add('a').Add('b')
    assert c.ToList() == ['a', 'b']
    c.Extend(['c', 'd'])
    assert c.ToList() == ['a', 'b', 'c', 'd']

def test_remove_at():
    c = Collection(10, 20, 30)
    c.RemoveAt(1)
    assert c.ToList() == [10, 30]
    with pytest.raises(IndexError):
        c.RemoveAt(10)

def test_index_of_and_contains():
    c = Collection('x', 'y', 'z')
    assert c.IndexOf('y') == 1
    assert not c.Contains('a')

def test_clear_and_is_empty():
    c = Collection(1, 2, 3)
    c.Clear()
    assert c.IsEmpty()
    assert c.Count() == 0

def test_find_and_flat_map():
    c = Collection(1, 2, 3, 4)
    assert c.Find(lambda x: x > 2) == 3
    flat = c.FlatMap(lambda x: [x, x*10])
    assert flat.ToList() == [1, 10, 2, 20, 3, 30, 4, 40]

def test_min_max_sample():
    c = Collection(3, 1, 4, 2)
    assert c.Min() == 1
    assert c.Max() == 4
    sample = c.Sample(2)
    assert len(sample.ToList()) == 2

def test_zip():
    c1 = Collection(1, 2, 3)
    c2 = Collection('a', 'b', 'c')
    zipped = c1.Zip(c2)
    assert zipped.ToList() == [(1, 'a'), (2, 'b'), (3, 'c')]

def test_all_any():
    c = Collection(2, 4, 6)
    assert c.All(lambda x: x % 2 == 0)
    assert c.Any(lambda x: x == 4)
    assert not c.Any(lambda x: x == 5)

def test_str_and_eq():
    c1 = Collection(1, 2, 3)
    c2 = Collection(1, 2, 3)
    c3 = Collection(4, 5, 6)
    assert str(c1) == "[1, 2, 3]"
    assert c1 == c2
    assert c1 != c3

def test_getitem_setitem_delitem():
    c = Collection('a', 'b', 'c')
    assert c[1] == 'b'
    c[1] = 'x'
    assert c[1] == 'x'
    del c[1]
    assert c.ToList() == ['a', 'c']

def test_slice_get_set():
    c = Collection(1, 2, 3, 4)
    assert c[1:3].ToList() == [2, 3]
    c[1:3] = ['x', 'y']
    assert c.ToList() == [1, 'x', 'y', 4]

def test_copy():
    c1 = Collection('foo', 'bar')
    c2 = c1.__copy__()
    assert c1 == c2
    c2.Add('baz')
    assert c1 != c2

def test_empty_collection_behavior():
    c = Collection()
    assert c.IsEmpty()
    assert c.ToList() == []
    assert c.Count() == 0
    assert c.Find(lambda x: True) is None
    with pytest.raises(ValueError):
        c.Min()
    with pytest.raises(ValueError):
        c.Max()

def test_insert_out_of_bounds():
    c = Collection(1, 2, 3)
    with pytest.raises(IndexError):
        c.Insert(10, 100)

def test_remove_nonexistent_item():
    c = Collection(1, 2, 3)
    result = c.Remove(10)
    assert c.ToList() == [1, 2, 3]

def test_metadata_content():
    c = Collection('a', 'b', 'c')
    meta = c.Metadata()
    assert 'CreateAt' in meta
    assert 'UpdatedAt' in meta
    assert 'Count' in meta
    assert meta['Count'] == 3
    assert meta['IsHomogeneous'] is True or meta['IsHomogeneous'] is False

def test_pretty_print(capsys):
    c = Collection(1, 2, 3)
    c.Print()
    captured = capsys.readouterr()
    assert "1" in captured.out and "2" in captured.out and "3" in captured.out

def test_chained_operations():
    c = Collection(1, 2, 3, 4, 5)
    c.Add(6).Remove(3).Insert(0, 0).Sort().Reverse()
    assert c.ToList() == [6, 5, 4, 2, 1, 0]

def test_fuse():
    c1 = Collection(1, 2)
    c2 = Collection(3, 4)
    c1.Fuse(c2)
    assert c1.ToList() == [1, 2, 3, 4]
    with pytest.raises(TypeError):
        c1.Fuse([5, 6])  # only accepts Collection

def test_slice_delete():
    c = Collection(1, 2, 3, 4, 5)
    del c[1:3]
    assert c.ToList() == [1, 4, 5]

def test_update_and_timestamps():
    c = Collection(1, 2, 3)
    old_update = c.updated_at
    c.Add(4)
    assert c.updated_at > old_update

def test_index_out_of_bounds_getitem():
    c = Collection(1, 2, 3)
    with pytest.raises(IndexError):
        _ = c[10]

def test_invalid_index_type():
    c = Collection(1, 2, 3)
    with pytest.raises(TypeError):
        _ = c['a']  # invalid index

def test_all_unique_property():
    c1 = Collection(1, 2, 3)
    c2 = Collection(1, 1, 2)
    assert c1.Metadata()['AllUnique'] is True
    assert c2.Metadata()['AllUnique'] is False

def test_multiple_operations_modification_count():
    c = Collection(1, 2, 3)
    initial_mod_count = c.modification_count

    # Perform multiple operations
    c.Add(4)
    c.Remove(2)
    c.Insert(0, 0)
    c.Sort()
    c.Reverse()
    c.Distinct()
    c.Extend([5, 6])
    c.RemoveAt(0)
    c.Clear()
    c.Add(7)
    c.Map(lambda x: x * 2)
    c.Filter(lambda x: x % 2 == 0)

    # The modification_count should be equal to the number of modifying operations
    expected_modifications = (
        1 +  # Add
        1 +  # Remove
        1 +  # Insert
        1 +  # Sort
        1 +  # Reverse
        1 +  # Distinct
        1 +  # Extend
        1 +  # RemoveAt
        1 +  # Clear
        1 +  # Add
        1 +  # Map
        1    # Filter
    )
    assert c.modification_count == initial_mod_count + expected_modifications