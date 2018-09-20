import math
import time

class World:
    def __init__(self, tiles, ants, bank=0):
        self.tiles = tiles # [tileObject, tileObject, ...]
        self.G = self.get_graph(tiles) # {'XXXX': {'YYYY': D1, 'ZZZZ': D2, ...}, 'YYYY': {'XXXX': D1, ...}}
        self.ants = ants # [antobject, antobject, ...]
        self.bank = bank # int

    def get_graph(self, tiles):
        self.G = {}
        for tile1 in self.tiles['paths']+self.tiles['beds']:
            self.G[tile1.id] = {}
            for tile2 in self.tiles['paths']+self.tiles['beds']:
                if not (tile1.id == tile2.id):
                    if abs(tile1.x - tile2.x) == 1 ^ abs(tile1.y - tile2.y) == 1:
                        self.G[tile1.id][tile2.id] = 1
                        # print((tile1.x, tile1.y), (tile2.x, tile2.y))
                        # time.sleep(1)
                    if abs(tile1.y - tile2.y) == 1 ^ abs(tile1.x - tile2.x) == 1:
                        self.G[tile1.id][tile2.id] = 1
                        # print((tile1.x, tile1.y), (tile2.x, tile2.y))
                    elif abs(tile1.x - tile2.x) == 1 and abs(tile1.y - tile2.y) == 1:
                        self.G[tile1.id][tile2.id] = math.sqrt(2)
                        # print((tile1.x, tile1.y), (tile2.x, tile2.y))
                        # time.sleep(1)
        return self.G

    def get_tile_from_id(self, ID):
        for tile in self.tiles['paths']+self.tiles['beds']:
            if tile.id == ID:
                return tile

    def get_tile_id(self, coords):
        x, y = coords[0], coords[1]
        for tile in self.tiles['paths']:
            if x == tile.x and y == tile.y:
                return tile.id
        for tile in self.tiles['beds']:
            if x == tile.x and y == tile.y:
                return tile.id
        for tile in self.tiles['workstations']:
            if x == tile.x and y == tile.y:
                return tile.id
        for tile in self.tiles['cafes']:
            if x == tile.x and y == tile.y:
                return tile.id

class Tile:
    def __init__(self, ID, x, y, kind, occupant, owner):
        self.id = ID
        self.x = x
        self.y = y
        self.kind = kind
        self.occupant = None
        self.owner = owner

    def occupy(self, ant):
        self.occupant = ant # ant may be None

def get_shortest_path(weighted_graph, start, end):
    """
    Calculate the shortest path for a directed weighted graph.

    Node can be virtually any hashable datatype.

    :param start: starting node
    :param end: ending node
    :param weighted_graph: {"node1": {"node2": "weight", ...}, ...}
    :return: ["START", ... nodes between ..., "END"] or None, if there is no
             path
    """
    # print(weighted_graph, start, end)
    # We always need to visit the start
    nodes_to_visit = {start}
    visited_nodes = set()
    # Distance from start to start is 0
    distance_from_start = {start: 0}
    tentative_parents = {}

    while nodes_to_visit:
        # The next node should be the one with the smallest weight
        current = min(
            [(distance_from_start[node], node) for node in nodes_to_visit]
        )[1]

        # The end was reached
        if current == end:
            break

        nodes_to_visit.discard(current)
        visited_nodes.add(current)

        edges = weighted_graph[current]
        unvisited_neighbours = set(edges).difference(visited_nodes)
        for neighbour in unvisited_neighbours:
            neighbour_distance = distance_from_start[current] + \
                                 edges[neighbour]
            if neighbour_distance < distance_from_start.get(neighbour,
                                                            float('inf')):
                distance_from_start[neighbour] = neighbour_distance
                tentative_parents[neighbour] = current
                nodes_to_visit.add(neighbour)

    return _deconstruct_path(tentative_parents, end)


def _deconstruct_path(tentative_parents, end):
    if end not in tentative_parents:
        return None
    cursor = end
    path = []
    while cursor:
        path.append(cursor)
        cursor = tentative_parents.get(cursor)
    # print(list(reversed(path)))
    return list(reversed(path))


def ttc(num, rl):# Translate to coordinates (index number, row length)
    x = num % rl
    y = int((num - x)/float(rl))
    return (x, y)

def revttc(coord, rl):
    x = coord[0]
    y = coord[1]
    i = y*rl + x
    return i
# G, world = setup_env()
# print(get_shortest_path(G, 0, 356))