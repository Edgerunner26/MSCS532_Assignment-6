"""
test_data_structures.py

Unit tests for data_structures.py.

Run with:  python -m unittest -v
"""

import unittest

from data_structures import (DynamicArray, Matrix, ArrayStack, ArrayQueue,
                             SinglyLinkedList, LinkedStack, LinkedQueue,
                             RootedTree)


class TestDynamicArray(unittest.TestCase):

    def test_append_get_set(self):
        a = DynamicArray()
        for i in range(10):
            a.append(i)
        self.assertEqual(len(a), 10)
        self.assertEqual(a.get(7), 7)
        a.set(7, 70)
        self.assertEqual(a.get(7), 70)
        self.assertGreaterEqual(a.capacity(), 10)

    def test_insert_and_delete_shift_items(self):
        a = DynamicArray()
        for x in [1, 2, 4]:
            a.append(x)
        a.insert(2, 3)
        a.insert(0, 0)
        self.assertEqual(list(a), [0, 1, 2, 3, 4])
        self.assertEqual(a.delete(0), 0)
        self.assertEqual(a.delete(3), 4)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(a.index_of(3), 2)
        self.assertEqual(a.index_of(99), -1)

    def test_shrinks_after_many_deletes(self):
        a = DynamicArray()
        for i in range(64):
            a.append(i)
        big = a.capacity()
        while len(a) > 2:
            a.pop()
        self.assertLess(a.capacity(), big)
        self.assertEqual(list(a), [0, 1])

    def test_bad_index(self):
        a = DynamicArray()
        with self.assertRaises(IndexError):
            a.get(0)
        with self.assertRaises(IndexError):
            a.insert(2, "x")
        with self.assertRaises(IndexError):
            a.pop()


class TestMatrix(unittest.TestCase):

    def test_get_set_and_shape(self):
        m = Matrix(2, 3)
        m.set(1, 2, 5)
        self.assertEqual(m.get(1, 2), 5)
        self.assertEqual(m.to_lists(), [[0, 0, 0], [0, 0, 5]])

    def test_rows_and_columns(self):
        m = Matrix.from_lists([[1, 2], [3, 4]])
        m.insert_row(0, [7, 8])
        m.insert_column(2, [0, 0, 0])
        self.assertEqual(m.to_lists(), [[7, 8, 0], [1, 2, 0], [3, 4, 0]])
        self.assertEqual(m.delete_row(1), [1, 2, 0])
        self.assertEqual(m.delete_column(0), [7, 3])
        self.assertEqual(m.to_lists(), [[8, 0], [4, 0]])

    def test_transpose(self):
        m = Matrix.from_lists([[1, 2, 3], [4, 5, 6]])
        self.assertEqual(m.transpose().to_lists(), [[1, 4], [2, 5], [3, 6]])

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            Matrix.from_lists([[1, 2], [3]])
        with self.assertRaises(IndexError):
            Matrix(2, 2).get(2, 0)


class TestStacksAndQueues(unittest.TestCase):

    def test_stacks_are_last_in_first_out(self):
        for stack in (ArrayStack(), LinkedStack()):
            for i in range(100):
                stack.push(i)
            self.assertEqual(stack.peek(), 99)
            self.assertEqual([stack.pop() for _ in range(100)], list(range(99, -1, -1)))
            self.assertTrue(stack.is_empty())
            with self.assertRaises(IndexError):
                stack.pop()

    def test_queues_are_first_in_first_out(self):
        for queue in (ArrayQueue(), LinkedQueue()):
            for i in range(100):
                queue.enqueue(i)
            self.assertEqual(queue.peek(), 0)
            self.assertEqual([queue.dequeue() for _ in range(100)], list(range(100)))
            self.assertTrue(queue.is_empty())
            with self.assertRaises(IndexError):
                queue.dequeue()

    def test_circular_queue_wraps_around(self):
        q = ArrayQueue(capacity=4)
        expected = []
        # Mixing adds and removes forces the front index to wrap past the end.
        for i in range(50):
            q.enqueue(i)
            expected.append(i)
            if i % 3 == 0:
                self.assertEqual(q.dequeue(), expected.pop(0))
        while not q.is_empty():
            self.assertEqual(q.dequeue(), expected.pop(0))
        self.assertEqual(expected, [])


class TestSinglyLinkedList(unittest.TestCase):

    def test_insert_and_traverse(self):
        ll = SinglyLinkedList()
        ll.insert_back(2)
        ll.insert_front(1)
        ll.insert_back(4)
        ll.insert_at(2, 3)
        self.assertEqual(ll.to_list(), [1, 2, 3, 4])
        self.assertEqual(ll.get(2), 3)
        self.assertEqual(ll.find(4), 3)
        self.assertEqual(ll.find(9), -1)

    def test_delete_keeps_tail_correct(self):
        ll = SinglyLinkedList([1, 2, 3])
        self.assertEqual(ll.delete_at(2), 3)
        ll.insert_back(5)
        self.assertEqual(ll.to_list(), [1, 2, 5])
        self.assertTrue(ll.delete_value(5))
        ll.insert_back(6)
        self.assertEqual(ll.to_list(), [1, 2, 6])
        self.assertFalse(ll.delete_value(42))

    def test_delete_until_empty(self):
        ll = SinglyLinkedList([1])
        ll.delete_front()
        self.assertTrue(ll.is_empty())
        self.assertIsNone(ll.tail)
        ll.insert_back(7)
        self.assertEqual(ll.to_list(), [7])

    def test_reverse(self):
        ll = SinglyLinkedList([1, 2, 3, 4])
        ll.reverse()
        self.assertEqual(ll.to_list(), [4, 3, 2, 1])
        ll.insert_back(0)
        self.assertEqual(ll.to_list(), [4, 3, 2, 1, 0])


class TestRootedTree(unittest.TestCase):

    def test_children_depth_and_preorder(self):
        t = RootedTree("A")
        b = t.add_child(t.root, "B")
        t.add_child(t.root, "C")
        d = t.add_child(b, "D")
        self.assertEqual(t.children(t.root), ["B", "C"])
        self.assertEqual(t.depth(d), 2)
        self.assertEqual(t.preorder(), ["A", "B", "D", "C"])
        self.assertEqual(len(t), 4)


if __name__ == "__main__":
    unittest.main()
