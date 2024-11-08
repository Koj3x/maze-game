import random


def create_maze_adjacency_graph(n):
    '''
    generates an n-by-n square maze using DFS
    returns adjacency graph where tiles are nodes denoted (x, y)
    '''
    adjacency_graph = {(x, y): [] for x in range(n) for y in range(n)}

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    stack = [(0, 0)]
    visited = set(stack)

    while stack:
        x, y = stack[-1]
        neighbors = []

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < n and (nx, ny) not in visited:
                neighbors.append((nx, ny))

        if neighbors:
            nx, ny = random.choice(neighbors)
            visited.add((nx, ny))
            stack.append((nx, ny))

            adjacency_graph[(x, y)].append((nx, ny))
            adjacency_graph[(nx, ny)].append((x, y))
        else:
            stack.pop()

    return adjacency_graph
