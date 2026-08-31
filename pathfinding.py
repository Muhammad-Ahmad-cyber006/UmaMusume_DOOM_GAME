from collections import deque
from functools import lru_cache

#this class implements a pathfinding algorithm for NPCs in the game.
# It uses a breadth-first search (BFS) approach to find the shortest path from a 
# starting position to a goal position on the games map. 
# The class constructs a graph representation of the map,
# where each walkable tile is a node and edges connect adjacent walkable tiles.
# The BFS algorithm explores the graph to determine the optimal path while avoiding obstacles
# and NPC positions.
class PathFinding:
    def __init__(self, game):
        self.game = game
        self.map = game.map.mini_map
        self.ways = [-1, 0], [0, -1], [1, 0], [0, 1], [-1, -1], [1, -1], [1, 1], [-1, 1]
        self.graph = {}
        self.get_graph()

    @lru_cache
    def get_path(self, start, goal):
        self.visited = self.bfs(start, goal, self.graph)
        path = [goal]
        step = self.visited.get(goal, start)

        while step and step != start:
            path.append(step)
            step = self.visited[step]
        return path[-1]

    def bfs(self, start, goal, graph):
        queue = deque([start])
        visited = {start: None}

        while queue:
            cur_node = queue.popleft()
            if cur_node == goal:
                break
            # get the next nodes from the graph for the current node
            # if the next node has not been visited and is not occupied by an NPC,\
            # add it to the queue and mark it as visited    
            next_nodes = graph.get(cur_node, [])

            for next_node in next_nodes:
                if next_node not in visited and next_node not in self.game.object_handler.npc_positions:
                    queue.append(next_node)
                    visited[next_node] = cur_node
        return visited

    def get_next_nodes(self, x, y):
        nodes = []
        for dx, dy in self.ways:
            nx, ny = x + dx, y + dy
            if (nx, ny) in self.game.map.world_map:
                continue
            if dx != 0 and dy != 0:
                # Donot allow cutting diagonally through a wall corner 
                # both cells flanking the diagonal step must also be open,
                # otherwise the diagonal step is blocked by a wall corner.
                if (x + dx, y) in self.game.map.world_map or (x, y + dy) in self.game.map.world_map:
                    continue
            nodes.append((nx, ny))
        return nodes

    def get_graph(self):
        for y, row in enumerate(self.map):
            for x, col in enumerate(row):
                if not col:
                    self.graph[(x, y)] = self.graph.get((x, y), []) + self.get_next_nodes(x, y)