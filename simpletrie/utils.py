from io import BytesIO
from itertools import chain
from typing import (
    Iterable,
    Iterator,
    Optional,
    Union,
    Sequence,
)


def bytes_to_nibbles(xs: Union[bytes, BytesIO]) -> Iterator[int]:
    for x in xs:
        yield x // 16
        yield x % 16


def nibbles_to_bytes(xs: Iterable[int]) -> Iterator[bytes]:
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


def hex_prefix(xs: Sequence[int], t: bool) -> Iterator[bytes]:
    flags = 2 if t else 0

    if len(xs) % 2 == 0:
        return nibbles_to_bytes(chain((flags, 0), xs))

    return nibbles_to_bytes(chain((flags + 1,), xs))


def indent(txt: str, prefix: str, rest_prefix: Optional[str]=None) -> str:
    def _g() -> Iterator[str]:
        nonlocal prefix

        lines = iter(txt.split('\n'))

        if rest_prefix is not None:
            yield prefix + next(lines)
            prefix = rest_prefix

        for l in lines:
            yield prefix + l

    return '\n'.join(_g())


def prefix_length(x: Iterable, y: Iterable) -> int:
    """
    Determines the length of any common prefix shared by the iterables ``x``
    and ``y``.
    """
    l = 0
    for i, j in zip(x, y):
        if i != j:
            break
        l += 1
    return l
