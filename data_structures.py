"""
data_structures.py

Elementary data structures built from scratch.

    DynamicArray       an array that grows and shrinks as needed
    Matrix             a 2D grid stored row by row in one flat array
    ArrayStack         a stack backed by an array
    ArrayQueue         a queue backed by a circular array
    SinglyLinkedList   a chain of nodes that each point to the next node
    LinkedStack        a stack backed by a singly linked list
    LinkedQueue        a queue backed by a singly linked list
    RootedTree         a tree that uses left child, right sibling links

To act like a real fixed size array, the array based classes only use a
Python list as a block of slots that is created once at a set size. They never
call append, insert, or pop on that list. All the shifting and resizing is
done by hand so the cost of each operation is easy to see.
"""


def _make_slots(capacity):
    """Create a block of empty slots. This plays the role of raw memory."""
    return [None] * capacity


# Arrays and matrices

class DynamicArray:
    """
    An array that doubles its capacity when full and halves it when only a
    quarter full.

    Operation          Time
    get / set          O(1)
    append             O(1) amortized
    insert(index)      O(n) because later items shift right
    delete(index)      O(n) because later items shift left
    search             O(n)
    """

    def __init__(self, capacity=4):
        if capacity < 1:
            raise ValueError("capacity must be at least 1.")
        self._data = _make_slots(capacity)
        self._size = 0

    def __len__(self):
        return self._size

    def __iter__(self):
        for i in range(self._size):
            yield self._data[i]

    def __repr__(self):
        return "DynamicArray(" + str(list(self)) + ")"

    def capacity(self):
        return len(self._data)

    def _check_index(self, index):
        if not 0 <= index < self._size:
            raise IndexError("index out of range.")

    def _resize(self, new_capacity):
        """Copy every item into a new block of slots. This is O(n)."""
        new_data = _make_slots(new_capacity)
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data

    def get(self, index):
        """Read the item at index. Arrays can jump straight to any slot."""
        self._check_index(index)
        return self._data[index]

    def set(self, index, value):
        """Replace the item at index."""
        self._check_index(index)
        self._data[index] = value

    def append(self, value):
        """Add to the end. Doubling means most appends never resize."""
        if self._size == len(self._data):
            self._resize(2 * len(self._data))
        self._data[self._size] = value
        self._size += 1

    def insert(self, index, value):
        """Insert at index and shift everything after it one slot right."""
        if not 0 <= index <= self._size:
            raise IndexError("index out of range.")
        if self._size == len(self._data):
            self._resize(2 * len(self._data))
        # Walk backward so we do not overwrite anything we still need.
        for i in range(self._size, index, -1):
            self._data[i] = self._data[i - 1]
        self._data[index] = value
        self._size += 1

    def delete(self, index):
        """Remove and return the item at index, shifting later items left."""
        self._check_index(index)
        value = self._data[index]
        for i in range(index, self._size - 1):
            self._data[i] = self._data[i + 1]
        self._size -= 1
        self._data[self._size] = None   # Clear the old slot for the garbage collector.
        # Shrink when only a quarter is used. Waiting until a quarter
        # (not a half) stops the array from resizing back and forth.
        if 0 < self._size <= len(self._data) // 4 and len(self._data) > 4:
            self._resize(len(self._data) // 2)
        return value

    def pop(self):
        """Remove and return the last item. O(1) amortized."""
        if self._size == 0:
            raise IndexError("pop from empty array.")
        return self.delete(self._size - 1)

    def index_of(self, value):
        """Return the first index holding value, or -1 if it is not there."""
        for i in range(self._size):
            if self._data[i] == value:
                return i
        return -1


class Matrix:
    """
    A rows by cols grid stored in row major order inside one flat array.
    The item at (r, c) lives at position r * cols + c.

    Operation              Time
    get / set              O(1)
    insert_row / delete_row        O(rows * cols) because the block is rebuilt
    insert_column / delete_column  O(rows * cols)
    transpose              O(rows * cols)
    """

    def __init__(self, rows, cols, fill=0):
        if rows < 0 or cols < 0:
            raise ValueError("rows and cols cannot be negative.")
        self.rows = rows
        self.cols = cols
        self._data = _make_slots(rows * cols)
        for i in range(rows * cols):
            self._data[i] = fill

    @classmethod
    def from_lists(cls, grid):
        """Build a Matrix from a list of equal length rows."""
        rows = len(grid)
        cols = len(grid[0]) if rows else 0
        m = cls(rows, cols)
        for r in range(rows):
            if len(grid[r]) != cols:
                raise ValueError("every row must have the same length.")
            for c in range(cols):
                m.set(r, c, grid[r][c])
        return m

    def _pos(self, r, c):
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise IndexError("matrix index out of range.")
        return r * self.cols + c

    def get(self, r, c):
        return self._data[self._pos(r, c)]

    def set(self, r, c, value):
        self._data[self._pos(r, c)] = value

    def to_lists(self):
        return [[self.get(r, c) for c in range(self.cols)] for r in range(self.rows)]

    def __repr__(self):
        return "Matrix(" + str(self.to_lists()) + ")"

    def insert_row(self, index, values):
        """Insert a new row before row index."""
        if not 0 <= index <= self.rows:
            raise IndexError("row index out of range.")
        if len(values) != self.cols:
            raise ValueError("row length must match the number of columns.")
        new_data = _make_slots((self.rows + 1) * self.cols)
        for r in range(self.rows + 1):
            for c in range(self.cols):
                if r < index:
                    new_data[r * self.cols + c] = self._data[r * self.cols + c]
                elif r == index:
                    new_data[r * self.cols + c] = values[c]
                else:
                    new_data[r * self.cols + c] = self._data[(r - 1) * self.cols + c]
        self._data = new_data
        self.rows += 1

    def delete_row(self, index):
        """Remove row index and return its values as a list."""
        if not 0 <= index < self.rows:
            raise IndexError("row index out of range.")
        removed = [self.get(index, c) for c in range(self.cols)]
        new_data = _make_slots((self.rows - 1) * self.cols)
        for r in range(self.rows - 1):
            source = r if r < index else r + 1
            for c in range(self.cols):
                new_data[r * self.cols + c] = self._data[source * self.cols + c]
        self._data = new_data
        self.rows -= 1
        return removed

    def insert_column(self, index, values):
        """Insert a new column before column index."""
        if not 0 <= index <= self.cols:
            raise IndexError("column index out of range.")
        if len(values) != self.rows:
            raise ValueError("column length must match the number of rows.")
        new_cols = self.cols + 1
        new_data = _make_slots(self.rows * new_cols)
        for r in range(self.rows):
            for c in range(new_cols):
                if c < index:
                    new_data[r * new_cols + c] = self._data[r * self.cols + c]
                elif c == index:
                    new_data[r * new_cols + c] = values[r]
                else:
                    new_data[r * new_cols + c] = self._data[r * self.cols + c - 1]
        self._data = new_data
        self.cols = new_cols

    def delete_column(self, index):
        """Remove column index and return its values as a list."""
        if not 0 <= index < self.cols:
            raise IndexError("column index out of range.")
        removed = [self.get(r, index) for r in range(self.rows)]
        new_cols = self.cols - 1
        new_data = _make_slots(self.rows * new_cols)
        for r in range(self.rows):
            for c in range(new_cols):
                source = c if c < index else c + 1
                new_data[r * new_cols + c] = self._data[r * self.cols + source]
        self._data = new_data
        self.cols = new_cols
        return removed

    def transpose(self):
        """Return a new Matrix with rows and columns swapped."""
        t = Matrix(self.cols, self.rows)
        for r in range(self.rows):
            for c in range(self.cols):
                t.set(c, r, self.get(r, c))
        return t


# Stacks and queues built on arrays

class ArrayStack:
    """
    Last in, first out. The top of the stack is the end of the array, so
    push and pop never have to shift anything.

    push   O(1) amortized (O(n) on the rare push that triggers a resize)
    pop    O(1) amortized
    peek   O(1)
    """

    def __init__(self, capacity=4):
        self._data = _make_slots(max(1, capacity))
        self._size = 0

    def __len__(self):
        return self._size

    def is_empty(self):
        return self._size == 0

    def _resize(self, new_capacity):
        new_data = _make_slots(new_capacity)
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data

    def push(self, value):
        if self._size == len(self._data):
            self._resize(2 * len(self._data))
        self._data[self._size] = value
        self._size += 1

    def pop(self):
        if self._size == 0:
            raise IndexError("pop from empty stack.")
        self._size -= 1
        value = self._data[self._size]
        self._data[self._size] = None
        if 0 < self._size <= len(self._data) // 4 and len(self._data) > 4:
            self._resize(len(self._data) // 2)
        return value

    def peek(self):
        if self._size == 0:
            raise IndexError("peek from empty stack.")
        return self._data[self._size - 1]


class ArrayQueue:
    """
    First in, first out, using a circular array.

    The front index moves forward as items leave, and it wraps around to
    slot 0 when it reaches the end. Because of this, dequeue never shifts
    the remaining items, which keeps it O(1).

    enqueue   O(1) amortized
    dequeue   O(1) amortized
    peek      O(1)
    """

    def __init__(self, capacity=4):
        self._data = _make_slots(max(1, capacity))
        self._front = 0
        self._size = 0

    def __len__(self):
        return self._size

    def is_empty(self):
        return self._size == 0

    def _resize(self, new_capacity):
        """Unwrap the circle into a new block so the front is at slot 0 again."""
        new_data = _make_slots(new_capacity)
        for i in range(self._size):
            new_data[i] = self._data[(self._front + i) % len(self._data)]
        self._data = new_data
        self._front = 0

    def enqueue(self, value):
        if self._size == len(self._data):
            self._resize(2 * len(self._data))
        back = (self._front + self._size) % len(self._data)
        self._data[back] = value
        self._size += 1

    def dequeue(self):
        if self._size == 0:
            raise IndexError("dequeue from empty queue.")
        value = self._data[self._front]
        self._data[self._front] = None
        self._front = (self._front + 1) % len(self._data)
        self._size -= 1
        if 0 < self._size <= len(self._data) // 4 and len(self._data) > 4:
            self._resize(len(self._data) // 2)
        return value

    def peek(self):
        if self._size == 0:
            raise IndexError("peek from empty queue.")
        return self._data[self._front]


# Linked lists

class Node:
    """One link in a singly linked list. It holds a value and the next node."""

    __slots__ = ("value", "next")

    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node


class SinglyLinkedList:
    """
    A chain of nodes. I keep both a head and a tail pointer so adding to
    either end is fast.

    insert_front       O(1)
    insert_back        O(1) thanks to the tail pointer
    insert_at(index)   O(n) because we walk to the spot first
    delete_front       O(1)
    delete_value       O(n)
    delete_at(index)   O(n)
    get(index)         O(n) because there is no direct jump like an array
    find / traverse    O(n)
    """

    def __init__(self, items=None):
        self.head = None
        self.tail = None
        self._size = 0
        if items is not None:
            for item in items:
                self.insert_back(item)

    def __len__(self):
        return self._size

    def __iter__(self):
        """Traverse the list from head to tail."""
        current = self.head
        while current is not None:
            yield current.value
            current = current.next

    def __repr__(self):
        return " -> ".join(str(v) for v in self) or "(empty)"

    def is_empty(self):
        return self._size == 0

    def to_list(self):
        return list(self)

    def insert_front(self, value):
        self.head = Node(value, self.head)
        if self.tail is None:
            self.tail = self.head
        self._size += 1

    def insert_back(self, value):
        node = Node(value)
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self._size += 1

    def _node_at(self, index):
        current = self.head
        for _ in range(index):
            current = current.next
        return current

    def insert_at(self, index, value):
        """Insert so the new value ends up at position index."""
        if not 0 <= index <= self._size:
            raise IndexError("index out of range.")
        if index == 0:
            self.insert_front(value)
        elif index == self._size:
            self.insert_back(value)
        else:
            before = self._node_at(index - 1)
            before.next = Node(value, before.next)
            self._size += 1

    def get(self, index):
        if not 0 <= index < self._size:
            raise IndexError("index out of range.")
        return self._node_at(index).value

    def find(self, value):
        """Return the position of the first match, or -1 if it is not there."""
        for i, item in enumerate(self):
            if item == value:
                return i
        return -1

    def delete_front(self):
        if self.head is None:
            raise IndexError("delete from empty list.")
        value = self.head.value
        self.head = self.head.next
        if self.head is None:
            self.tail = None
        self._size -= 1
        return value

    def delete_at(self, index):
        """Remove and return the value at position index."""
        if not 0 <= index < self._size:
            raise IndexError("index out of range.")
        if index == 0:
            return self.delete_front()
        before = self._node_at(index - 1)
        target = before.next
        before.next = target.next
        if target is self.tail:
            self.tail = before
        self._size -= 1
        return target.value

    def delete_value(self, value):
        """Remove the first node holding value. Return True if one was removed."""
        previous = None
        current = self.head
        while current is not None:
            if current.value == value:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                if current is self.tail:
                    self.tail = previous
                self._size -= 1
                return True
            previous = current
            current = current.next
        return False

    def reverse(self):
        """Flip the direction of every link. O(n) time and O(1) extra space."""
        previous = None
        current = self.head
        self.tail = self.head
        while current is not None:
            following = current.next
            current.next = previous
            previous = current
            current = following
        self.head = previous


class LinkedStack:
    """A stack where the top is the head of a linked list. All operations O(1)."""

    def __init__(self):
        self._list = SinglyLinkedList()

    def __len__(self):
        return len(self._list)

    def is_empty(self):
        return self._list.is_empty()

    def push(self, value):
        self._list.insert_front(value)

    def pop(self):
        if self._list.is_empty():
            raise IndexError("pop from empty stack.")
        return self._list.delete_front()

    def peek(self):
        if self._list.is_empty():
            raise IndexError("peek from empty stack.")
        return self._list.head.value


class LinkedQueue:
    """
    A queue where items join at the tail and leave from the head.
    All operations are O(1) in the worst case, with no resizing at all.
    """

    def __init__(self):
        self._list = SinglyLinkedList()

    def __len__(self):
        return len(self._list)

    def is_empty(self):
        return self._list.is_empty()

    def enqueue(self, value):
        self._list.insert_back(value)

    def dequeue(self):
        if self._list.is_empty():
            raise IndexError("dequeue from empty queue.")
        return self._list.delete_front()

    def peek(self):
        if self._list.is_empty():
            raise IndexError("peek from empty queue.")
        return self._list.head.value


# Rooted trees (optional part)

class TreeNode:
    """
    A tree node that uses the left child, right sibling idea. Each node only
    needs two links no matter how many children it has: one to its first
    child and one to its next sibling. It also keeps a link to its parent.
    """

    __slots__ = ("value", "parent", "left_child", "right_sibling")

    def __init__(self, value, parent=None):
        self.value = value
        self.parent = parent
        self.left_child = None
        self.right_sibling = None


class RootedTree:
    """
    A rooted tree with any number of children per node.

    add_child     O(number of children) because the new child goes to the end
    children      O(number of children)
    depth         O(height)
    preorder      O(n)
    """

    def __init__(self, root_value):
        self.root = TreeNode(root_value)
        self._size = 1

    def __len__(self):
        return self._size

    def add_child(self, parent, value):
        """
        Attach a new child under parent and return the new node.

        I add the child at the end of the sibling chain so children stay in
        the order they were added. Putting it at the front would be O(1), but
        the order would come out backward.
        """
        child = TreeNode(value, parent)
        if parent.left_child is None:
            parent.left_child = child
        else:
            current = parent.left_child
            while current.right_sibling is not None:
                current = current.right_sibling
            current.right_sibling = child
        self._size += 1
        return child

    def children(self, node):
        """Return the values of node's children in the order they are linked."""
        result = []
        current = node.left_child
        while current is not None:
            result.append(current.value)
            current = current.right_sibling
        return result

    def depth(self, node):
        """Count the edges from node up to the root."""
        d = 0
        while node.parent is not None:
            node = node.parent
            d += 1
        return d

    def preorder(self):
        """Visit each node before its children. I use a stack to avoid recursion."""
        result = []
        stack = ArrayStack()
        stack.push(self.root)
        while not stack.is_empty():
            node = stack.pop()
            result.append(node.value)
            # Push the siblings in reverse so the first child comes out first.
            kids = []
            current = node.left_child
            while current is not None:
                kids.append(current)
                current = current.right_sibling
            for kid in reversed(kids):
                stack.push(kid)
        return result


if __name__ == "__main__":
    arr = DynamicArray()
    for x in [10, 20, 30]:
        arr.append(x)
    arr.insert(1, 15)
    print("Array after insert:", arr)
    removed = arr.delete(0)
    print("Deleted", removed, "and now the array is:", arr)

    m = Matrix.from_lists([[1, 2], [3, 4]])
    m.insert_row(1, [9, 9])
    print("Matrix with new row:", m, "| transpose:", m.transpose())

    s = ArrayStack()
    for x in "abc":
        s.push(x)
    print("Stack pops:", s.pop(), s.pop(), s.pop())

    q = ArrayQueue()
    for x in "abc":
        q.enqueue(x)
    print("Queue dequeues:", q.dequeue(), q.dequeue(), q.dequeue())

    ll = SinglyLinkedList([1, 2, 3])
    ll.insert_front(0)
    ll.insert_at(2, 99)
    ll.delete_value(2)
    print("Linked list:", ll)

    t = RootedTree("CEO")
    cto = t.add_child(t.root, "CTO")
    t.add_child(t.root, "CFO")
    t.add_child(cto, "Dev Lead")
    print("Tree preorder:", t.preorder())
