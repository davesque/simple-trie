from hypothesis import (
    given,
    strategies as st,
)
import pytest

from simpletrie.utils import (
    bytes_to_nibbles,
    nibbles_to_bytes,
)


byte_strs = st.binary()
nibble_lists = st.lists(st.integers(min_value=0, max_value=15))


@given(byte_strs)
def test_bytes_to_nibbles_to_bytes(byte_str):
    assert b''.join(nibbles_to_bytes(bytes_to_nibbles(byte_str))) == byte_str


@given(nibble_lists)
def test_nibbles_to_bytes_to_nibbles(nibble_list):
    if len(nibble_list) % 2 == 1:
        with pytest.raises(ValueError, match='odd number of nibbles'):
            tuple(nibbles_to_bytes(nibble_list))

        return

    byte_str = b''.join(nibbles_to_bytes(nibble_list))
    assert list(bytes_to_nibbles(byte_str)) == nibble_list
