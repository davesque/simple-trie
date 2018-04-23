from hypothesis import (
    given,
    strategies as st,
)
import pytest

from simpletrie.trie import (
    SimpleTrie,
)


key_value_pairs = st.tuples(st.binary(max_size=100), st.binary())


@given(st.lists(key_value_pairs, max_size=100, unique_by=lambda pair: pair[0]))
def test_simple_trie_properties(pairs):
    t = SimpleTrie()

    assert len(t) == 0

    for i, (key, value) in enumerate(pairs):
        with pytest.raises(KeyError, match='Value not found'):
            t[key]
        with pytest.raises(KeyError, match='Value not found'):
            del t[key]

        t[key] = value

        assert t[key] == value
        assert len(t) == i + 1

    for i, (key, value) in enumerate(pairs):
        del t[key]

        with pytest.raises(KeyError, match='Value not found'):
            t[key]
        with pytest.raises(KeyError, match='Value not found'):
            del t[key]
        assert len(t) == len(pairs) - i - 1

    assert len(t) == 0
