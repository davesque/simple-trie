from .utils import (
    bytes_to_nibbles,
    indent,
    nibbles_to_bytes,
)


class Node:
    __slots__ = tuple()


class Leaf(Node):
    __slots__ = ('key', 'value')

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value

    @property
    def is_empty(self):
        return self.value is None

    def __repr__(self):  # pragma: no coverage
        repr_key = repr(self.key)

        return indent(
            repr(self.value),
            '{}: '.format(repr_key),
            '{}| '.format(' ' * len(repr_key)),
        )


class Extension(Node):
    __slots__ = ('key', 'node')

    def __init__(self, key=None, node=None):
        self.key = key
        self.node = node

    @property
    def is_empty(self):
        return self.node is None

    def __repr__(self):  # pragma: no coverage
        repr_key = repr(self.key)

        return indent(
            repr(self.node),
            '{}: '.format(repr_key),
            '{}| '.format(' ' * len(repr_key)),
        )


class Branch(Node):
    __slots__ = ('nodes', 'value')

    def __init__(self, nodes=None, value=None):
        self.nodes = [None] * 16
        self.value = value

    def __getitem__(self, key):
        return self.nodes[key]

    def __setitem__(self, key, value):
        self.nodes[key] = value

    @property
    def is_empty(self):
        return all(n is None for n in self.nodes) and self.value is None

    def __repr__(self):  # pragma: no coverage
        node_reprs = []

        for i, n in enumerate(self.nodes):
            if n is None:
                continue

            indented = indent(
                repr(n),
                '{}: '.format(hex(i)[-1:].upper()),
                ' | ',
            )

            node_reprs.append(indented)

        if node_reprs:
            return '{} (\n{}\n)'.format(repr(self.value), '\n'.join(node_reprs))

        return repr(self.value)


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

    def _len(self, node):
        """
        Returns the number of nodes under ``node`` in which a value is stored.
        """
        if node is None:
            return 0

        if node.value is not None:
            return 1 + sum(self._len(n) for n in node.nodes)

        return sum(self._len(n) for n in node.nodes)

    def _size(self, node):
        """
        Returns the number of nodes under ``node``.
        """
        if node is None:
            return 0

        return 1 + sum(self._len(n) for n in node.nodes)

    def __getitem__(self, key):
        return self._get(self._root, tuple(bytes_to_nibbles(key)), 0)

    def __setitem__(self, key, value):
        self._set(self._root, tuple(bytes_to_nibbles(key)), 0, value)

    def __delitem__(self, key):
        self._del(self._root, tuple(bytes_to_nibbles(key)), 0)

    def __len__(self):
        return self._len(self._root)

    @property
    def size(self):
        return self._size(self._root)

    def __repr__(self):  # pragma: no coverage
        return repr(self._root)
