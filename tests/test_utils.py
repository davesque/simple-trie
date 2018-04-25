from hypothesis import (
    given,
    strategies as st,
)
import pytest

from simpletrie.utils import (
    bytes_to_nibbles,
    hex_prefix,
    indent,
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


@pytest.mark.parametrize(
    'input, expected',
    (
        (b'', ()),
        (b'\x2c', (2, 12)),
        (b'\xff\x00', (15, 15, 0, 0)),
    ),
)
def test_bytes_to_nibbles(input, expected):
    assert tuple(bytes_to_nibbles(input)) == expected


@pytest.mark.parametrize(
    'input, expected',
    (
        ((), b''),
        ((2, 12), b'\x2c'),
        ((15, 15, 0, 0), b'\xff\x00'),
    ),
)
def test_nibbles_to_bytes(input, expected):
    assert b''.join(nibbles_to_bytes(input)) == expected


@given(nibble_lists)
def test_hex_prefix(nibble_list):
    bytes_with_flag = b''.join(hex_prefix(nibble_list, True))
    bytes_without_flag = b''.join(hex_prefix(nibble_list, False))

    nibbles_with_flag = list(bytes_to_nibbles(bytes_with_flag))
    nibbles_without_flag = list(bytes_to_nibbles(bytes_without_flag))

    if len(nibble_list) % 2 == 0:
        assert nibbles_with_flag[0] == 2
        assert nibbles_without_flag[0] == 0

        assert nibbles_with_flag[1] == 0
        assert nibbles_without_flag[1] == 0

        assert nibbles_with_flag[2:] == nibble_list
        assert nibbles_without_flag[2:] == nibble_list
    else:
        assert nibbles_with_flag[0] == 3
        assert nibbles_without_flag[0] == 1

        assert nibbles_with_flag[1:] == nibble_list
        assert nibbles_without_flag[1:] == nibble_list


def test_indent():
    short_txt = """
foo
"""[1:-1]

    med_txt = """
foo
bar
"""[1:-1]

    long_txt = """
foo
bar
baz
bing
bust
"""[1:-1]

    assert indent(short_txt, '  1. ') == """
  1. foo
"""[1:-1]
    assert indent(short_txt, '  1. ', '     ') == """
  1. foo
"""[1:-1]

    assert indent(med_txt, '  1. ') == """
  1. foo
  1. bar
"""[1:-1]
    assert indent(med_txt, '  1. ', '     ') == """
  1. foo
     bar
"""[1:-1]

    assert indent(long_txt, '  1. ') == """
  1. foo
  1. bar
  1. baz
  1. bing
  1. bust
"""[1:-1]
    assert indent(long_txt, '  1. ', '     ') == """
  1. foo
     bar
     baz
     bing
     bust
"""[1:-1]
