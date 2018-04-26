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


@given(nodes, leaves)
def test_delete_insert_get_leaves(node, leaf):
    try:
        node -= leaf.key
    except KeyError:
        # Value with leaf's key may not be present in node
        pass

    # Key should definitely not exist in node or node should be None
    if node is not None:
        with pytest.raises(KeyError):
            node.get(leaf.key)

    # Insert should not complain
    node += leaf

    # Key should definitely be mapped to value
    assert node.get(leaf.key) == leaf.value


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
