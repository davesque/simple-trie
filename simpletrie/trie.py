import abc

from .utils import (
    bytes_to_nibbles,
    indent,
    prefix_length,
)


class Node(abc.ABC):
    __slots__ = tuple()

    @property
    @abc.abstractmethod
    def is_empty(self):
        """
        Returns a boolean value that indicates if this node can be safely
        deleted.
        """
        pass

    @abc.abstractmethod
    def get(self, key):
        """
        Returns any value mapped to by ``key`` in this node.
        """
        pass

    @abc.abstractmethod
    def insert(self, leaf: 'Leaf'):
        """
        Returns the result of inserting a leaf into this node.  Must return new
        object.
        """
        pass

    def __add__(self, leaf: 'Leaf'):
        return self.insert(leaf)

    def __eq__(self, other):
        return (
            type(self) is type(other) and
            all(
                getattr(self, a) == getattr(other, a)
                for a in self.__slots__
            )
        )

    @abc.abstractmethod
    def copy(self):
        """
        Creates a copy of this node.
        """
        pass


class Leaf(Node):
    __slots__ = ('key', 'value')

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value

    @property
    def is_empty(self):
        return self.value is None

    def head(self, i=1):
        """
        Returns the initial ``i`` items in this node's key.
        """
        return self.key[:i]

    def tail(self, i=1):
        """
        Returns a new leaf node with the same value as this node and excluding
        the initial ``i`` items in this node's key.
        """
        return type(self)(self.key[i:], self.value)

    def get(self, key):
        if self.key == key:
            return self.value

        raise KeyError('Key not found')

    def insert(self, leaf: 'Leaf'):
        # Special cases
        if self.key == leaf.key:
            # Leaves share same key or are both shallow (zero-length)
            return leaf

        if len(self.key) == 0:
            # Inserting deep leaf into shallow leaf
            return Branch(value=self.value) + leaf

        if len(leaf.key) == 0:
            # Inserting shallow leaf into deep leaf
            return Branch(value=leaf.value) + self

        # General cases
        l = prefix_length(self.key, leaf.key)

        if l > 0:
            # Nodes share common prefix
            return Extension(
                self.key[:l],
                Leaf(self.key[l:], self.value) +
                Leaf(leaf.key[l:], leaf.value),
            )

        # Nodes share no common prefix
        return Branch() + self + leaf

    def copy(self):
        return type(self)(self.key, self.value)

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

    def get(self, key):
        i = len(self.key)
        head, tail = key[:i], key[i:]

        if self.key == head:
            return self.node.get(tail)

        raise KeyError('Key not found')

    def insert(self, other):
        # Special cases

        len_self = len(self.key)

        if self.key == other.key:
            # Nodes share same key
            return self.node + Leaf((), other.value)

        if len_self == 0:
            # Self is zero-length
            return self.node + other

        if len(other.key) == 0:
            # Inserting zero-length leaf
            branch = Branch(value=other.value)
            if len_self == 1:
                branch[self.key[0]] = self.node
            else:
                branch[self.key[0]] = Extension(self.key[:1], self.node)

            return branch

        # General cases

        # Determine length of common prefix
        i = 0
        for k1, k2 in zip(self.key, other.key):
            if k1 != k2:
                break
            i += 1

        if i > 0:
            # Nodes share common prefix
            return Extension(
                self.key[:i],
                Extension(self.key[i:], self.node) + Leaf(other.key[i:], other.value),
            )

        # Nodes share no common prefix
        branch = Branch()
        if len_self == 1:
            branch[self.key[0]] = self.node
        else:
            branch[self.key[0]] = Extension(self.key[i:], self.node)
        branch[other.key[0]] = Leaf(other.key[1:], other.value)

        return branch

    def copy(self):
        return type(self)(self.key, self.node.copy())

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
        if nodes is None:
            self.nodes = [None] * 16
        else:
            self.nodes = nodes

        self.value = value

    def __getitem__(self, key):
        return self.nodes[key]

    def __setitem__(self, key, value):
        self.nodes[key] = value

    @property
    def is_empty(self):
        return all(n is None for n in self.nodes) and self.value is None

    def get(self, key):
        if len(key) == 0:
            return self.value

        head, tail = key[0], key[1:]
        curr = self.nodes[head]
        if curr is not None:
            return curr.get(tail)

        raise KeyError('Key not found')

    def insert(self, other):
        branch = Branch(self.nodes[:], self.value)

        if len(other.key) == 0:
            branch.value = other.value
            return branch

        head, tail = other.key[0], other.key[1:]
        curr = branch[head]

        if curr is None:
            branch[head] = Leaf(tail, other.value)
        else:
            branch[head] = curr + Leaf(tail, other.value)

        return branch

    def __eq__(self, other):
        return (
            type(self) is type(other) and
            self.value == other.value and
            all(n1 == n2 for n1, n2 in zip(self.nodes, other.nodes))
        )

    def copy(self):
        return type(self)(
            [n.copy() if n is not None else n for n in self.nodes],
            self.value,
        )

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
        self._root = Leaf((), None)

    def __getitem__(self, key):
        return self._root.get(tuple(bytes_to_nibbles(key)))

    def __setitem__(self, key, value):
        self._root += Leaf(
            tuple(bytes_to_nibbles(key)),
            value,
        )

    def __delitem__(self, key):
        self._root -= tuple(bytes_to_nibbles(key))

    def __len__(self):
        return len(self._root)

    def __repr__(self):  # pragma: no coverage
        return repr(self._root)
