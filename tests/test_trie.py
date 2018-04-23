from hypothesis import (
    given,
    strategies as st,
)
import pytest

from simpletrie.trie import (
    SimpleTrie,
)


key_value_pairs = st.tuples(st.binary(max_size=32), st.binary())


@given(st.lists(key_value_pairs, max_size=10, unique_by=lambda pair: pair[0]))
def test_simple_trie_basic_usage_properties(pairs):
    t = SimpleTrie()

    assert len(t) == 0

    for i, (key, value) in enumerate(pairs):
        t[key] = value
        assert len(t) == i + 1

    for key, value in pairs:
        assert t[key] == value
        del t[key]

    assert len(t) == 0


def test_simple_trie_get_non_existant_keys():
    t = SimpleTrie()

    with pytest.raises(KeyError, match='Value not found for key'):
        t[b'']

    with pytest.raises(KeyError, match='Value not found for key'):
        t[b'\xff']


def test_simple_trie_delete_non_existant_keys():
    t = SimpleTrie()

    with pytest.raises(KeyError, match='Value not found for key'):
        del t[b'']

    with pytest.raises(KeyError, match='Value not found for key'):
        del t[b'\xff']
