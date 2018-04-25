from hypothesis import (
    given,
    settings,
    strategies as st,
)
import pytest

from simpletrie.trie import (
    Branch,
    Extension,
    Leaf,
    SimpleTrie,
)


def test_leaf_insert():
    # Leaves have same key
    assert Leaf((10,), b'\x00') + Leaf((10,), b'\x01') == Leaf((10,), b'\x01')

    # First leaf is zero-length
    assert Leaf((), b'\x00') + Leaf((), b'\x01') == Leaf((), b'\x01')
    assert Leaf((), b'\x00') + Leaf((10,), b'\x01') == Branch(
        [None] * 10 + [Leaf((), b'\x01')] + [None] * 5,
        b'\x00',
    )

    # First leaf is not zero-length
    assert Leaf((10,), b'\x00') + Leaf((), b'\x01') == Branch(
        [None] * 10 + [Leaf((), b'\x00')] + [None] * 5,
        b'\x01',
    )

    # Leaves share common prefix
    assert Leaf((10, 11), b'\x00') + Leaf((10, 12), b'\x01') == Extension((10,), Branch(
        [None] * 11 + [Leaf((), b'\x00'), Leaf((), b'\x01')] + [None] * 2,
    ))

    # Leaves share no common prefix
    assert Leaf((11,), b'\x00') + Leaf((12,), b'\x01') == Branch(
        [None] * 11 + [Leaf((), b'\x00'), Leaf((), b'\x01')] + [None] * 2,
    )


key_value_pairs = st.tuples(st.binary(max_size=100), st.binary())


@settings(deadline=None)
@given(st.lists(key_value_pairs, max_size=100, unique_by=lambda pair: pair[0]))
def test_simple_trie_properties(pairs):
    t = SimpleTrie()

    # Trie should be empty and contain only root node
    assert len(t) == 0
    cur_size = 1
    assert t.size == cur_size

    for i, (key, value) in enumerate(pairs):
        # For each key and value added...

        # Attempting to look up or delete non-existant key should cause error
        with pytest.raises(KeyError, match='Value not found'):
            t[key]
        with pytest.raises(KeyError, match='Value not found'):
            del t[key]

        # Should be able to set a value for a key
        t[key] = value
        if key != b'':
            # Setting anything other than root key should change node count
            cur_size += 1

        # Value should be present at expected key
        assert t[key] == value

        # There should be i + 1 values in trie
        assert len(t) == i + 1

        # There should be expected number of nodes in trie
        assert t.size == cur_size

    for i, (key, value) in enumerate(pairs):
        # Should be able to delete value at key
        del t[key]
        if key != b'':
            # Deleting anything other than root key should change node count
            cur_size -= 1

        # Attempting to look up or delete non-existant key should cause error
        with pytest.raises(KeyError, match='Value not found'):
            t[key]
        with pytest.raises(KeyError, match='Value not found'):
            del t[key]

        # There should be one less value in trie after deletion
        assert len(t) == len(pairs) - i - 1

        # There should be expected number of nodes in trie
        assert t.size == cur_size

    # Trie should be empty and contain only root node
    assert len(t) == 0
    assert cur_size == 1
