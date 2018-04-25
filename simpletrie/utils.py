from itertools import chain
from typing import (
    Iterable,
    Sequence,
)


Bytes = Iterable[bytes]
Nibbles = Iterable[int]
SizedNibbles = Sequence[int]


def bytes_to_nibbles(xs: Bytes) -> Nibbles:
    for x in xs:
        yield x // 16
        yield x % 16


def nibbles_to_bytes(xs: Nibbles) -> Bytes:
    odd, even = True, False
    b = 0

    for x in xs:
        b += 16 * x if odd else x

        if even:
            yield b.to_bytes(1, 'big')
            b = 0

        odd, even = even, odd

    if even:
        raise ValueError('Input array had odd number of nibbles')


def hex_prefix(xs: SizedNibbles, t: bool) -> Bytes:
    flags = 2 if t else 0

    if len(xs) % 2 == 0:
        return nibbles_to_bytes(chain((flags, 0), xs))

    return nibbles_to_bytes(chain((flags + 1,), xs))


def indent(txt, prefix, rest_prefix=None):
    def _g():
        nonlocal prefix

        lines = iter(txt.split('\n'))

        if rest_prefix is not None:
            yield prefix + next(lines)
            prefix = rest_prefix

        for l in lines:
            yield prefix + l

    return '\n'.join(_g())
