from hypothesis import (
    given,
    settings,
    strategies as st,
)
import pytest

from simpletrie.trie import (
    SimpleTrie,
)


key_value_pairs = st.tuples(st.binary(max_size=100), st.binary())


@settings(deadline=None)
@given(st.lists(key_value_pairs, max_size=100, unique_by=lambda pair: pair[0]))
def test_simple_trie_properties(pairs):
    t = SimpleTrie()

    assert len(t) == 0

    cur_size = 1
    assert t.size == cur_size

    for i, (key, value) in enumerate(pairs):
        with pytest.raises(KeyError, match='Value not found'):
            t[key]
        with pytest.raises(KeyError, match='Value not found'):
            del t[key]

        t[key] = value
        if key != b'':
            cur_size += 1

        assert t[key] == value
        assert len(t) == i + 1
        assert t.size == cur_size

    for i, (key, value) in enumerate(pairs):
        del t[key]
        if key != b'':
            cur_size -= 1

        with pytest.raises(KeyError, match='Value not found'):
            t[key]
        with pytest.raises(KeyError, match='Value not found'):
            del t[key]
        assert len(t) == len(pairs) - i - 1
        assert t.size == cur_size

    assert len(t) == 0
    assert cur_size == 1
