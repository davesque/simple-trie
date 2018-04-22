from eth_utils.crypto import keccak_256 as sha3
from rlp import encode as rlp


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

    def __init__(self, value=b''):
        self.hashes = [b''] * 16
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
    def __init__(self):
        root = Branch()
        root_hsh = sha3(rlp(tuple(root)))

        self._db = {
            root_hsh: root,
        }

    def _set(self, hsh, key, value):
        try:
            # Fetch node from db
            node = self._db[hsh]
        except KeyError:
            # If not found in db, default to new branch node
            node_ = Branch(None)
        else:
            # If found in db, make copy for mutation
            node_ = node.copy()

        if len(key) == 0:
            # If all nibbles in the key have been traversed, this node should
            # store the key's value
            node_.value = value
        else:
            # If nibbles remain in key, recurse with hash associated with first
            # remaining nibble.  Consider other remaining nibbles to be
            # remaining key.  Re-use value.
            child_hsh = self._set(node[key[0]], key[1:], value)
            node_[key[0]] = child_hsh

        hsh_ = sha3(rlp(tuple(node_)))
        self.db[hsh_] = node_

        return hsh_
