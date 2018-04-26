import functools

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
from simpletrie.utils import (
    bytes_to_nibbles,
)


def unary(f):
    """
    Converts a callable into a unary version of itself.
    """
    @functools.wraps(f)
    def f_(args):
        return f(*args)

    return f_


def make_branch_strategy(s):
    return st.tuples(
        st.lists(s, min_size=16, max_size=16),
        st.one_of(st.none(), values),
    ).map(unary(Branch))


def make_extension_strategy(s):
    return st.tuples(
        non_zero_nibbles,
        make_branch_strategy(s),
    ).map(unary(Extension))


nibbles = st.binary().map(bytes_to_nibbles).map(tuple)
non_zero_nibbles = st.binary(min_size=1).map(bytes_to_nibbles).map(tuple)
values = st.binary()

leaves = st.tuples(
    nibbles,
    values,
).map(unary(Leaf))

nodes = st.recursive(
    leaves,
    lambda s: st.one_of(
        # Recursion could be branch
        make_branch_strategy(s),
        # Recursion could be extension
        make_extension_strategy(s),
    ),
    max_leaves=50,
)

extensions = make_extension_strategy(nodes)
branches = make_branch_strategy(nodes)


@settings(max_examples=25)
@given(nodes)
def test_node_copy_properties(node):
    copy = node.copy()

    assert node == copy
    assert node is not copy


@settings(max_examples=25)
@given(nodes)
def test_node_radd_properties(node):
    assert None + node == node


@pytest.mark.parametrize(
    'node, expected',
    (
        (Leaf((), b'\x00'), False),
        (Leaf((), None), True),
        (Leaf((0,), b'\x00'), False),
        (Leaf((0, 1), None), True),
        (Extension((), None), True),
        (Extension((1,), None), True),
        (Extension((), Branch()), False),
        (Extension((1,), Branch()), False),
        (Branch(), True),
        (Branch() + Leaf((1,), b'\x00'), False),
        (Branch(value=b'\x00'), False),
    ),
)
def test_node_is_empty(node, expected):
    assert node.is_empty is expected


@pytest.mark.parametrize(
    'node, expected',
    (
        (Leaf((), b'\x00'), True),
        (Leaf((0,), b'\x00'), False),
        (Leaf((0, 1), None), False),
        (Extension((), None), True),
        (Extension((0,), Branch()), False),
        (Extension((0, 1), None), False),
    ),
)
def test_node_is_shallow(node, expected):
    assert node.is_shallow is expected


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
    'node, i, tail',
    (
        (Leaf((10, 11, 12), b'\x00'), None, Leaf((11, 12), b'\x00')),
        (Leaf((10, 11, 12), b'\x00'), 0, Leaf((10, 11, 12), b'\x00')),
        (Leaf((10, 11, 12), b'\x00'), 1, Leaf((11, 12), b'\x00')),
        (Leaf((10, 11, 12), b'\x00'), 2, Leaf((12,), b'\x00')),
        (Leaf((10, 11, 12), b'\x00'), 3, Leaf((), b'\x00')),
        (Extension((10, 11, 12), Branch()), None, Extension((11, 12), Branch())),
        (Extension((10, 11, 12), Branch()), 0, Extension((10, 11, 12), Branch())),
        (Extension((10, 11, 12), Branch()), 1, Extension((11, 12), Branch())),
        (Extension((10, 11, 12), Branch()), 2, Extension((12,), Branch())),
        (Extension((10, 11, 12), Branch()), 3, Branch()),
    ),
)
def test_node_tail(node, i, tail):
    if i is None:
        assert node.tail() == tail
    else:
        assert node.tail(i) == tail


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
    branch = (
        Branch() +
        Leaf((), b'\x00') +
        Leaf((), b'\x01')
    )
    leaf = Leaf((10,), b'\x02')

    actual = Extension((10,), branch) + leaf
    expected = Extension(
        (10,),
        branch + leaf.tail(),
    )

    assert actual == expected


key_value_pairs = st.tuples(st.binary(max_size=100), st.binary())


@settings(deadline=None)
@given(st.lists(key_value_pairs, max_size=100, unique_by=lambda pair: pair[0]))
def test_simple_trie_properties(pairs):
    t = SimpleTrie()

    # Trie should be empty and contain only root node
    assert len(t) == 0

    for i, (key, value) in enumerate(pairs):
        # For each key and value added...

        # Attempting to look up or delete non-existant key should cause error
        with pytest.raises(KeyError):
            t[key]
        with pytest.raises(KeyError):
            del t[key]

        # Should be able to set a value for a key
        t[key] = value

        # Value should be present at expected key
        assert t[key] == value

        # There should be i + 1 values in trie
        assert len(t) == i + 1

    for i, (key, value) in enumerate(pairs):
        # Should be able to delete value at key
        del t[key]

        # Attempting to look up or delete non-existant key should cause error
        with pytest.raises(KeyError):
            t[key]
        with pytest.raises(KeyError):
            del t[key]

        # There should be one less value in trie after deletion
        assert len(t) == len(pairs) - i - 1

    # Trie should be empty and contain only root node
    assert len(t) == 0
