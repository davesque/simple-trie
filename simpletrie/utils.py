def bytes_to_nibbles(byte_str):
    for b in byte_str:
        yield b // 16
        yield b % 16


def nibbles_to_bytes(nibbles):
    odd, even = True, False
    b = 0

    for n in nibbles:
        b += 16 * n if odd else n

        if even:
            yield b
            b = 0

        odd, even = even, odd

    if even:
        raise ValueError('Input array had odd number of nibbles')
