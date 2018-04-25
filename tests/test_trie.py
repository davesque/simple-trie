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


@pytest.mark.parametrize(
    'node',
    (
        Leaf((), None),
        Extension((), None),
        Branch(),
    ),
)
def test_node_radd(node):
    assert None + node == node


@pytest.mark.parametrize(
    'leaf, expected',
    (
        (Leaf((), b'\x00'), False),
        (Leaf((), None), True),
        (Leaf((0,), b'\x00'), False),
        (Leaf((0, 1), None), True),
    ),
)
def test_leaf_is_empty(leaf, expected):
    assert leaf.is_empty is expected


@pytest.mark.parametrize(
    'leaf, expected',
    (
        (Leaf((), b'\x00'), True),
        (Leaf((0,), b'\x00'), False),
        (Leaf((0, 1), None), False),
    ),
)
def test_leaf_is_shallow(leaf, expected):
    assert leaf.is_shallow is expected


@pytest.mark.parametrize(
    'leaf, i, head',
    (
        (Leaf((10, 11, 12), b'\x00'), None, (10,)),
        (Leaf((10, 11, 12), b'\x00'), 0, ()),
        (Leaf((10, 11, 12), b'\x00'), 1, (10,)),
        (Leaf((10, 11, 12), b'\x00'), 2, (10, 11)),
        (Leaf((10, 11, 12), b'\x00'), 3, (10, 11, 12)),
    ),
)
def test_leaf_head(leaf, i, head):
    if i is None:
        assert leaf.head() == head
    else:
        assert leaf.head(i) == head


@pytest.mark.parametrize(
    'leaf, i, tail',
    (
        (Leaf((10, 11, 12), b'\x00'), None, Leaf((11, 12), b'\x00')),
        (Leaf((10, 11, 12), b'\x00'), 0, Leaf((10, 11, 12), b'\x00')),
        (Leaf((10, 11, 12), b'\x00'), 1, Leaf((11, 12), b'\x00')),
        (Leaf((10, 11, 12), b'\x00'), 2, Leaf((12,), b'\x00')),
        (Leaf((10, 11, 12), b'\x00'), 3, Leaf((), b'\x00')),
    ),
)
def test_leaf_tail(leaf, i, tail):
    if i is None:
        assert leaf.tail() == tail
    else:
        assert leaf.tail(i) == tail


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


def test_extension_insert():
    # Nodes have same key
    branch = Branch()
    branch[10] = Leaf((), b'\x00')
    branch[11] = Leaf((), b'\x01')

    actual = Extension((10,), branch) + Leaf((10,), b'\x02')

    expected = branch.copy()
    expected.value = b'\x02'

    assert actual == expected

    # Extension has zero-length key
    branch = Branch()
    branch[10] = Leaf((), b'\x00')
    branch[11] = Leaf((), b'\x01')

    actual = Extension((), branch) + Leaf((10,), b'\x02')

    expected = branch.copy()
    expected[10] = Leaf((), b'\x02')

    assert actual == expected


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
