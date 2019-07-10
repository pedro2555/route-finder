from unittest import TestCase

from fsnavigator_map import FsNavigatorMap, Node

class TestFsNavigatorMap(FsNavigatorMap):
    def _read_file(self):
        return [
            'PESUL	40.881944	-8.115000	14	W2	    L	PRT	    41.273000	-8.687833	0	    Y	VIS	    40.723417	-7.885833	9500	Y',
            'PRT	    41.273000	-8.687833	14	W2	    L	0	                                    N	PESUL	40.881944	-8.115000	9500	Y',
            'PRT	43.809833	11.200500	14	Q25	L				0	N	LOMED	44.027222	11.003333	11000	Y',
            'EKMAR	38.557500	-9.521389	14	Y207	B	ODLIX	38.678889	-9.317222	9500	N	0	                                    N',
            'ODLIX	38.678889	-9.317222	14	Y207	B	LIS	38.887750	-9.162806	9500	N	EKMAR	38.557500	-9.521389	9500	Y'
        ]

class TestParseAirwayNode(TestCase):
    def setUp(self):
        self.map = TestFsNavigatorMap()

    def test_allNodesHaveRequiredInfo(self):
        for node in self.map.nodes.values():
            self.assertIsNotNone(node.name)
            self.assertIsNone(node.via)
            self.assertIsNone(node.via_type)

    def test_nodesAreAccessiblePerName(self):
        for name, lat, lng in [('PESUL', 40.881944, -8.115000), ('PRT', 41.273000, -8.687833)]:
            node = self.map.nodes[name]
            self.assertEqual(node.name, name)
            self.assertEqual(node.x, lat)
            self.assertEqual(node.y, lng)

    def test_neighboursAreAccessibleViaNode(self):
        pesul = self.map.nodes['PESUL']
        prt = self.map.nodes['PRT']
        neighbours = self.map.neighbours[pesul]
        self.assertEqual(len(neighbours), 2)
        for _, neighbour in neighbours:
            if neighbour == prt:
                self.assertEqual(neighbour.via, 'W2')
                self.assertEqual(neighbour.via_type, 'L')
                return
        self.assertFalse(True)

        ekmar = self.map.nodes['EKMAR']
        neighbours = self.map.neighbours[ekmar]
        self.assertEqual(len(neighbours), 0)
