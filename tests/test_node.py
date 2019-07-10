from unittest import TestCase

from fsnavigator_map import Node

class TestNode(TestCase):
    def test_latOrLngNotANumber_raisesValueError(self):
        with self.assertRaises(ValueError):
            Node('', '', 0)
            Node('', 0, '',)

    def test_nodesWithSwappedLatLng_dontCollide(self):
        node_a1 = Node(1, 2, 'a')
        node_a2 = Node(2, 1, 'a')
        node_b = Node(2, 1, 'b')
        self.assertNotEqual(node_a1.__hash__(), node_a2.__hash__())
        self.assertNotEqual(node_a1, node_a2)

        self.assertNotEqual(node_a2.__hash__(), node_b.__hash__())
        self.assertNotEqual(node_a2, node_b)
