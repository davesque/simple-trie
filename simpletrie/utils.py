from typing import Iterable


Bytes = Iterable[bytes]
Nibbles = Iterable[int]


def bytes_to_nibbles(bs: Bytes) -> Nibbles:
    for b in bs:
        yield b // 16
        yield b % 16


def nibbles_to_bytes(ns: Nibbles) -> Bytes:
    odd, even = True, False
    b = 0

    for n in ns:
        b += 16 * n if odd else n

        if even:
            yield b.to_bytes(1, 'big')
            b = 0

        odd, even = even, odd

    if even:
        raise ValueError('Input array had odd number of nibbles')
