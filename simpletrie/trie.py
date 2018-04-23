from eth_utils.crypto import keccak_256 as kec
from simplerlp import encode as rlp

from .utils import (
    bytes_to_nibbles,
    nibbles_to_bytes,
)


class Node:
    __slots__ = tuple()


class Branch(Node):
    __slots__ = ('nodes', 'value')

    def __init__(self, nodes=None, value=None):
        if nodes is None:
            self.nodes = [None] * 16
        else:
            self.nodes = nodes

        self.value = value

    def __getitem__(self, key):
        return self.nodes[key]

    def __setitem__(self, key, value):
        self.nodes[key] = value

    def copy(self):
        return type(self)(self.nodes[:], self.value)

    @property
    def is_empty(self):
        return all(n is None for n in self.nodes) and self.value is None

    def __iter__(self):
        yield from self.nodes
        yield self.value

    def __repr__(self):
        node_reprs = []

        for i, n in enumerate(self.nodes):
            prefix = '  {}: '.format(hex(i)[-1:])
            repr_lines = repr(n).split('\n')
            indented_repr = '\n'.join(prefix + l for l in repr_lines)

            node_reprs.append(indented_repr)

        return '{} (\n{}\n)'.format(repr(self.value), '\n'.join(node_reprs))


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

        hsh_ = kec(rlp(tuple(node_)))
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


class SimpleTrie:
    __slots__ = ('_root',)

    def __init__(self):
        self._root = Branch()

    def _get(self, node, key, i):
        """
        Under ``node``, get the value keyed by the nibble array ``key[i:]``.
        """
        try:
            nib = key[i]
        except IndexError:
            if node.value is None:
                raise KeyError('Value not found for key {}'.format(
                    repr(b''.join(nibbles_to_bytes(key))),
                ))
            return node.value

        node_ = node[nib]
        if node_ is None:
            raise KeyError('Value not found for key {}'.format(
                repr(b''.join(nibbles_to_bytes(key))),
            ))

        return self._get(node_, key, i + 1)

    def _set(self, node, key, i, value):
        """
        Under ``node``, store ``value`` keyed by the nibble array ``key[i:]``.
        """
        try:
            nib = key[i]
        except IndexError:
            node.value = value
            return

        node_ = node[nib]
        if node_ is None:
            node_ = Branch()
            node[nib] = node_

        self._set(node_, key, i + 1, value)

    def _del(self, node, key, i):
        """
        Under ``node``, delete the value keyed by the nibble array ``key[i:]``.
        """
        try:
            nib = key[i]
        except IndexError:
            if node.value is None:
                raise KeyError('Value not found for key {}'.format(
                    repr(b''.join(nibbles_to_bytes(key))),
                ))
            node.value = None
            return

        node_ = node[nib]
        if node_ is None:
            raise KeyError('Value not found for key {}'.format(
                repr(b''.join(nibbles_to_bytes(key))),
            ))

        self._del(node_, key, i + 1)
        if node_.is_empty:
            node[nib] = None

    def __getitem__(self, key):
        return self._get(self._root, tuple(bytes_to_nibbles(key)), 0)

    def __setitem__(self, key, value):
        self._set(self._root, tuple(bytes_to_nibbles(key)), 0, value)

    def __delitem__(self, key):
        self._del(self._root, tuple(bytes_to_nibbles(key)), 0)

    def __repr__(self):
        return repr(self._root)
