# Eclipse Depths - A* Pathfinding

from __future__ import annotations
import heapq
from typing import Callable


def astar(grid_passable: Callable[[int, int], bool],
          start: tuple[int, int],
          goal:  tuple[int, int],
          max_steps: int = 400) -> list[tuple[int, int]]:
    """
    Returns a list of (col, row) grid cells from start to goal (exclusive of start).
    grid_passable(col, row) should return True if that cell can be walked on.
    """
    if start == goal:
        return []

    def h(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_heap: list[tuple[float, tuple[int, int]]] = []
    heapq.heappush(open_heap, (h(start, goal), start))
    came_from:  dict[tuple, tuple | None] = {start: None}
    g_score:    dict[tuple, float]        = {start: 0.0}
    steps = 0

    NEIGHBOURS = [(0, -1), (0, 1), (-1, 0), (1, 0),
                  (-1, -1), (1, -1), (-1, 1), (1, 1)]
    DIAG_COST = 1.414

    while open_heap and steps < max_steps:
        steps += 1
        _, current = heapq.heappop(open_heap)

        if current == goal:
            path: list[tuple[int, int]] = []
            node: tuple[int, int] | None = current
            while node and node != start:
                path.append(node)
                node = came_from[node]
            path.reverse()
            return path

        cx, cy = current
        for dx, dy in NEIGHBOURS:
            nx, ny = cx + dx, cy + dy
            neighbour = (nx, ny)
            if not grid_passable(nx, ny):
                continue
            cost = DIAG_COST if dx != 0 and dy != 0 else 1.0
            new_g = g_score[current] + cost
            if new_g < g_score.get(neighbour, float("inf")):
                came_from[neighbour] = current
                g_score[neighbour]   = new_g
                f = new_g + h(neighbour, goal)
                heapq.heappush(open_heap, (f, neighbour))

    return []  # no path found
