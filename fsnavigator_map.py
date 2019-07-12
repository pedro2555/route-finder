""" This module implements the RouteMap interface to be injected to RouteFinder.

It provides airway information data from FS Navigator AIRAC files.

FS Navigator files:

    `AIRWAY.txt`

        It is a TAB delimited file. The compilation of the elements are the followings:
        1 - the name of the point
        2 - latitude of the point
        3 - longitude of the point
        4 - ignored
        5 - the name of the airway
        6 - the type of the airway
        7 - the previous point along the airway
        8 - latitude of the previous point
        9 - longitude of the previous point
        10 - minimum altitude from the previous point
        11 - airway can be used from this point to the previous
        12 - the next point along the airway
        13 - latitude of the next point
        14 - longitude of the next point
        15 - minimum altitude to the next point
        16 - airway can be used from this point to the previous
        12-16 is the same as 7-11 but for the next point
        (source: https://forums.vatsim.net/viewtopic.php?p=372310)

"""
from collections import defaultdict
import math

class FsNavigatorMap():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        file_lines = self._read_file()
        self.nodes, self.neighbours = self._parse_lines(file_lines)

    def _read_file(self):
        lines = []
        with open('fsnavigator/Bin/AIRWAY.txt', 'r') as f:
            lines = f.readlines()
        return lines

    def _parse_lines(self, lines):
        lines = [line.strip().split('\t') for line in lines if not line.strip().startswith(';')]
        nodes = dict()
        neighbours = defaultdict(list)
        for line in lines:
            line = [i.strip() for i in line]
            node = line[:6]
            node_neighbours = line[6:]
            node = self._parse_airway_node(node)
            node_neighbours = list(self._parse_airway_neighbours(node_neighbours))
            for neighbour in node_neighbours:
                neighbour.via = node.via
                neighbour.via_type = node.via_type
            node_neighbours = [(self._calc_cost(node.x, node.y, neighbour.x, neighbour.y), neighbour) for neighbour in node_neighbours]
            neighbours[node] = [*neighbours[node], *node_neighbours]
            nodes[node.name] = Node(node.x, node.y, node.name)
        return nodes, neighbours

    def _calc_cost(self, *args):
        try:
            if len(args) == 2:
                args = (*args[0], *args[1])
            xa, ya, xb, yb = args
        except TypeError as crap:
            raise ValueError() from crap

        R = 6378137 # earth radius in meters
        # (source: https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html)

        phi1, phi2 = math.radians(xa), math.radians(xb)
        dphi       = math.radians(xb - xa)
        dlambda    = math.radians(yb - ya)

        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2

        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _parse_airway_node(self, node):
        """PESUL	40.881944	-8.115000	14	W2	    L"""
        name, lat, lng, _, via, via_type = node
        return Node(float(lat), float(lng), name, via, via_type)

    def _parse_airway_neighbours(self, neighbours):
        split_at = 2 if neighbours[0] == '0' else 5
        left = neighbours[:split_at]
        right = neighbours[split_at:]
        _neighbours = list()
        for item in [left, right]:
            if len(item) != 5:
                continue

            name, lat, lng, _, can_fly = item
            can_fly = can_fly == 'Y'
            if not can_fly:
                continue

            _neighbours.append(Node(float(lat), float(lng), name))
        return _neighbours

class RouteMap():
    def __init__(self, *args, map, **kwargs):
        super().__init__(*args, **kwargs)

        self._map = map
        self._neighbours = map.neighbours

    def get_node_neighbours(self, node):
        return self._map.neighbours[node]

    def get_node(self, name):
        return self._map.nodes[name]

class Node:
    def __init__(self, x, y, name, via=None, via_type=None):
        self.x = float(x)
        self.y = float(y)
        self.name = name
        self.via = via
        self.via_type = via_type

    def __eq__(self, other):
        if not isinstance(other, Node):
            return false

        return self.name == other.name and self.x == other.x and self.y == other.y

    def __gt__(self, other):
        return self.name > other.name

    def __hash__(self):
        return int(self.name.__hash__() * self.x**5 * self.y * 13)

    def __repr__(self):
        return self.name
