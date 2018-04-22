from eth_utils.crypto import keccak_256 as sha3
from simplerlp import encode as rlp

from .utils import (
    bytes_to_nibbles,
    nibbles_to_bytes,
)


class Node:
    __slots__ = tuple()


# class Leaf(Node):
#     __slots__ = ('subkey', 'value')

#     def __init__(self, subkey, value):
#         self.subkey = subkey
#         self.value = value


# class Extension(Node):
#     __slots__ = ('subkey', 'hsh')

#     def __init__(self, subkey, hsh):
#         self.subkey = subkey
#         self.hsh = hsh


class Branch(Node):
    __slots__ = ('hashes', 'value')

    def __init__(self, hashes=None, value=b''):
        if hashes is None:
            self.hashes = [b''] * 16
        else:
            self.hashes = hashes

        self.value = value

    def __getitem__(self, key):
        return self.hashes[key]

    def __setitem__(self, key, value):
        self.hashes[key] = value

    def copy(self):
        return type(self)(self.hashes[:], self.value)

    def __iter__(self):
        for hsh in self.hashes:
            yield hsh

        yield self.value


class Trie:
    __slots__ = ('_root_hsh', '_db')

    def __init__(self):
        self._root_hsh = b''
        self._db = {}

        self[b''] = b''

    def _get(self, hsh, nibs):
        # Fetch node from db
        node = self._db[hsh]

        if len(nibs) == 0:
            # If all nibbles in the key have been traversed, this node should
            # contain the key's value
            return node.value

        # If nibbles remain in key, recurse with hash associated with first
        # remaining nibble.  Consider other remaining nibbles to be
        # remaining key.
        return self._get(node[nibs[0]], nibs[1:])

    def _set(self, hsh, nibs, value):
        try:
            # Fetch node from db
            node = self._db[hsh]
        except KeyError:
            # If not found in db, default to new branch node
            node_ = Branch()
        else:
            # If found in db, make copy for mutation
            node_ = node.copy()

        if len(nibs) == 0:
            # If all nibbles in the key have been traversed, this node should
            # store the key's value
            node_.value = value
        else:
            # If nibbles remain in key, recurse with hash associated with first
            # remaining nibble.  Consider other remaining nibbles to be
            # remaining key.  Re-use value.
            child_hsh = self._set(node[nibs[0]], nibs[1:], value)
            node_[nibs[0]] = child_hsh

        hsh_ = sha3(rlp(tuple(node_)))
        self._db[hsh_] = node_

        return hsh_

    def __getitem__(self, key):
        return self._get(
            self._root_hsh,
            bytes_to_nibbles(key),
        )

    def __setitem__(self, key, value):
        self._root_hsh = self._set(
            self._root_hsh,
            bytes_to_nibbles(key),
            value,
        )
