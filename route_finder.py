import heapq
from heuristics import haversine
from fsnavigator_map import RouteMap, Node

class Heuristics:
    def astar_heuristic(self, *args):
        return haversine(*args)

class HeapQueue:
    def __init__(self, items):
        self._heap = items
        heapq.heapify(self._heap)

    def push(self, item):
        heapq.heappush(self._heap, item)

    def pop(self):
        return heapq.heappop(self._heap)

    def pushpop(self, item):
        return heapq.heappushpop(self._heap, item)

    def __len__(self):
        return len(self._heap)

class RouteFinder(RouteMap, Heuristics):
    def __init__(self, *args, start, end, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_node = start
        self.end_node = end
        self.closed_list = {}

    def find(self):
        open_list = HeapQueue([(0, 0, self.start_node, None)])
        self.closed_list = {}

        while len(open_list) > 0:
            node_f, node_g, node, parent = open_list.pop()
            self.closed_list[node] = (node_g, parent)

            if node == self.end_node:
                self.end_node = node
                return

            for neighbour_g, neighbour in super().get_node_neighbours(node):
                if neighbour in self.closed_list:
                    continue

                h = super().astar_heuristic(neighbour.x, neighbour.y, self.end_node.x, self.end_node.y)
                g = neighbour_g + node_g
                f = g + h

                open_list.push((f, g, neighbour, node))
        raise RuntimeError('Unable to find route.')

    @property
    def nodes(self):
        return self._path_to(self.end_node)

    def _path_to(self, node):
        result = []
        while node:
            result.append(node)
            _, node = self.closed_list[node]
        result.reverse()
        return result

    @property
    def atc_route(self):
        node = self.end_node
        nodes = []
        while node:
            nodes.append(node)
            _, node = self.closed_list[node]

        result = []
        via = None
        for node in nodes:
            if node.via == via:
                continue

            if node.via:
                result.append(f'{node.via} {node.name}')
            else:
                result.append(node.name)
            via = node.via
        result.reverse()
        return ' '.join(result)
