import pygame
import sys
from collections import defaultdict
import heapq
from random import choice
import math
import time

from maze_gen import create_maze_adjacency_graph

pygame.init()
pygame.mixer.init()

# sounds
sound1 = pygame.mixer.Sound('assets/hello.mp3')
sound2 = pygame.mixer.Sound('assets/laugh.mp3')
sound3 = pygame.mixer.Sound('assets/ambiance.mp3')
win = pygame.mixer.Sound('assets/win.mp3')
gameover = pygame.mixer.Sound('assets/gameover.mp3')

# constants
TILE_SIZE = 40
FPS = 60

MOVE_SPEED = 2
NPC_MOVE_SPEED = 1.5
PLAYER_RADIUS = TILE_SIZE / 2 - 10

MAZE_LEN = 20
WIDTH = TILE_SIZE * MAZE_LEN
HEIGHT = TILE_SIZE * MAZE_LEN

# images
npc1 = pygame.image.load("assets/ghost.png")
npc1 = pygame.transform.scale(npc1, (0.8 * TILE_SIZE, 0.8 * TILE_SIZE))
npc2 = pygame.image.load("assets/eloot.png")
npc2 = pygame.transform.scale(npc2, (1.2 * TILE_SIZE, 1.2 * TILE_SIZE))

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
BLUE = (0, 0, 255)
LIGHT_BLUE = (150, 200, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# init
window_size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("maze")
clock = pygame.time.Clock()

# sample adjacency graph for tiles
# tile_graph = {
#     (0, 0): [(1, 0)],
#     (1, 0): [(0, 0), (2, 0)],
#     (2, 0): [(1, 0), (2, 1)],
#     (3, 0): [(3, 1)],
#     (0, 1): [(1, 1), (0, 2)],
#     (1, 1): [(0, 1), (2, 1), (1, 2)],
#     (2, 1): [(1, 1), (2, 0)],
#     (3, 1): [(3, 0), (3, 2)],
#     (0, 2): [(0, 1), (0, 3)],
#     (1, 2): [(1, 1), (1, 3), (2, 2)],
#     (2, 2): [(1, 2), (3, 2)],
#     (3, 2): [(2, 2), (3, 1)],
#     (0, 3): [(0, 2)],
#     (1, 3): [(1, 2), (2, 3)],
#     (2, 3): [(1, 3), (3, 3)],
#     (3, 3): [(2, 3)]
# }

# generate adjacency graph for tiles
tile_graph = create_maze_adjacency_graph(MAZE_LEN)

# generate edges (between adjacent but not connected tiles)
tile_edge_graph = defaultdict(list)

for node, adjs in tile_graph.items():
    edges = [
        i for i in [
            (node[0] -
             1,
             node[1]),
            (node[0] +
             1,
             node[1]),
            (node[0],
             node[1] -
             1),
            (node[0],
             node[1] +
             1)] if (
            0 <= i[0] <= MAZE_LEN -
            1) and (
                0 <= i[1] <= MAZE_LEN -
            1)]
    tile_edge_graph[node] = [edge for edge in edges if edge not in adjs]

# dict -> (x, y): top elft coordinates
tile_coords = {}

for node in tile_graph.keys():
    tile_coords[node] = (node[0] * TILE_SIZE, node[1] * TILE_SIZE)

# dict -> (x, y): center coordinates
tile_center_coords = {}

for k, v in tile_coords.items():
    tile_center_coords[k] = (v[0] + TILE_SIZE / 2, v[1] + TILE_SIZE / 2)

# generates coords of edges


def make_edges(g):
    '''
    takes in adjacency graph, g
    returns list of edges e.g. [(starting_coordinate, ending_coordinate), (...), (...), ...]
    '''
    edges = set()

    for node, adjs in g.items():
        # print('e', node, adjs, type(adjs[0]))
        for adj in adjs:
            # print('ee', adj)
            # start_pos, end_pos = _, _
            node_xy = tile_coords[node]
            adj_xy = tile_coords[tuple(adj)]

            if node[0] == adj[0]:
                start_pos = (node_xy[0], max(node_xy[1], adj_xy[1]))
                end_pos = (node_xy[0] + TILE_SIZE, max(node_xy[1], adj_xy[1]))

                if (start_pos, end_pos) not in edges and (
                        end_pos, start_pos) not in edges:
                    edges.add((start_pos, end_pos))

            elif node[1] == adj[1]:
                start_pos = (max(node_xy[0], adj_xy[0]), node_xy[1])
                end_pos = (max(node_xy[0], adj_xy[0]), node_xy[1] + TILE_SIZE)

                if (start_pos, end_pos) not in edges and (
                        end_pos, start_pos) not in edges:
                    edges.add((start_pos, end_pos))

    return edges


# generate edges using tile graph
edges = make_edges(tile_edge_graph)

# nick - dijkstra implementation of shortest path


def dijkstra(G, s, t, move_speed=NPC_MOVE_SPEED):
    '''
    uses dijkstra's algorithm to find shortest path
    returns direction that the npc should move using relative position of npc and next tile
    '''
    # s is npc location, t is player location
    dist = defaultdict(lambda: float('inf'))
    dist[s] = 0.0
    paths = defaultdict(list)
    paths[s].append(s)
    Q = [(0, s, None)]

    while Q:
        current_dist, node, pnode = heapq.heappop(Q)
        paths[node] = paths[pnode] + [node]
        if current_dist > dist[node]:
            continue
        for neighbor in G[node]:
            ndist = 1
            if ndist < dist[neighbor]:
                dist[neighbor] = ndist
                heapq.heappush(Q, (ndist, neighbor, node))

    paths.pop(None)

    if s[0] == paths[t][1][0] - 1:
        return (move_speed, 0)
    elif s[0] == paths[t][1][0] + 1:
        return (-1 * move_speed, 0)
    elif s[1] == paths[t][1][1] - 1:
        return (0, move_speed)
    elif s[1] == paths[t][1][1] + 1:
        return (0, -1 * move_speed)

# print(npc_dir(tile_graph, (0,0), (3,3)))


def A_star(G, npc, player):
    '''
    uses A* algorithm to find shortest path
    returns direction that the npc should move using relative position of npc and next tile

    !! was not able to implement because of complications with npc getting stuck
    !! future goal for project would be to get this working
    !! for now, both npcs use dijkstra's
    '''
    E = set()
    E.add(npc)
    stack = [(npc, math.sqrt((player[0] - npc[0])**2 + (player[1] - npc[1])**2))]
    path = []
    while len(stack) != 0 and player not in path:
        a = min(stack, key=lambda x: x[1])
        stack.remove(a)
        path.append(a[0])
        for i in G[a[0]]:
            if i not in E:
                stack.append(
                    (i, math.sqrt((player[0] - i[0])**2 + (player[1] - i[1])**2)))
                E.add(i)

    if npc[0] == path[1][0] - 1:
        return (NPC_MOVE_SPEED, 0)
    elif npc[0] == path[1][0] + 1:
        return (-1 * NPC_MOVE_SPEED, 0)
    elif npc[1] == path[1][1] - 1:
        return (0, NPC_MOVE_SPEED)
    elif npc[1] == path[1][1] + 1:
        return (0, -1 * NPC_MOVE_SPEED)


input_dir = None  # directional input provided by player (w, a, s, d)
move_dir = (0, 0)  # direction that player actually moves

player_pos = (0.5 * TILE_SIZE, 0.5 * TILE_SIZE)  # coordinates of player
player_tile = (0, 0)  # tile where player was last seen
player_visible = True  # whether player is visible

# list of npcs -> each element is in the form [coordinates, direction]
# where both are xy-tuples
npcs = [[[TILE_SIZE * (0.5), TILE_SIZE * (MAZE_LEN - 0.5)], [0, 0]],
        [[TILE_SIZE * (MAZE_LEN - 0.5), TILE_SIZE * (0.5)], [0, 0]]]

# determines whether player or npc is at the center of a tile and can reevaluate direction
# if so, outputs the tile


def is_corner(pos, r=2):
    for target in tile_graph.keys():
        target_coord = tile_center_coords[target]
        if abs(
                pos[0] -
                target_coord[0]) < r and abs(
                pos[1] -
                target_coord[1]) < r:
            return target

# evaluates distance between two points


def dist(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

# check if player has reached end zone


def check_win(pos, r=5):
    target = tile_center_coords[(MAZE_LEN - 1, MAZE_LEN - 1)]
    return abs(pos[0] - target[0]) < r and abs(pos[1] - target[1]) < r

# check if player has collided with any npc


def game_over(player_pos, npc_pos, r=5):
    return abs(
        player_pos[0] -
        npc_pos[0]) < r and abs(
        player_pos[1] -
        npc_pos[1]) < r


start_time = time.time()

# game loop
running = True

while running:
    # parse through detected events
    for event in pygame.event.get():
        # option to quit game window
        if event.type == pygame.QUIT:
            running = False

        # detects w, a, s, d keypresses and changes input direction vector
        # accordingly
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                input_dir = (0, -1)

            if event.key == pygame.K_a:
                input_dir = (-1, 0)

            if event.key == pygame.K_s:
                input_dir = (0, 1)

            if event.key == pygame.K_d:
                input_dir = (1, 0)

    # sets to tile where player is located; None otherwise
    player_corner = is_corner(player_pos)
    visible = not (move_dir == (0, 0))  # player is visible only when moving

    for i in range(len(npcs)):
        npc_pos = npcs[i][0]
        npc_tile = is_corner(npc_pos)

        # updates npc move direction if npc is found to be at a tile center
        if npc_tile:
            if visible:
                try:
                    npcs[i][1] = A_star(
                        tile_graph, npc_tile, player_tile, move_speed=NPC_MOVE_SPEED + (i == 1))
                except BaseException:
                    continue
            else:
                try:
                    npcs[i][1] = A_star(tile_graph, npc_tile, (0, 0))
                except BaseException:
                    continue

        # updates npc position
        npcs[i][0] = (
            npcs[i][0][0] +
            npcs[i][1][0],
            npcs[i][0][1] +
            npcs[i][1][1])

    # sets player movement direction if player is found to be at tile center
    if player_corner:
        player_tile = player_corner

        if input_dir:
            if (player_tile[0] +
                input_dir[0], player_tile[1] +
                    input_dir[1]) in tile_graph[player_tile]:
                player_pos = (
                    player_pos[0] + input_dir[0],
                    player_pos[1] + input_dir[1])
                move_dir = (
                    input_dir[0] * MOVE_SPEED,
                    input_dir[1] * MOVE_SPEED)
            else:
                move_dir = (0, 0)
        else:
            move_dir = (0, 0)

    # reset screen
    screen.fill(WHITE)

    # draws green end zone
    pygame.draw.rect(screen,
                     GREEN,
                     pygame.Rect(tile_coords[(MAZE_LEN - 1,
                                              MAZE_LEN - 1)][0],
                                 tile_coords[(MAZE_LEN - 1,
                                              MAZE_LEN - 1)][1],
                                 TILE_SIZE,
                                 TILE_SIZE))

    # draws maze edges
    for edge in edges:
        pygame.draw.line(screen, GREY, edge[0], edge[1], 2)

    # updates player coordiantes if player is moving, i.e. visible
    if visible:
        player_pos = (player_pos[0] + move_dir[0], player_pos[1] + move_dir[1])

    # changes color of player depending on visibility
    # light blue indicates 'invisible'
    if not visible:
        pygame.draw.circle(screen, LIGHT_BLUE, player_pos, PLAYER_RADIUS, 0)
    else:
        pygame.draw.circle(screen, BLUE, player_pos, PLAYER_RADIUS, 0)

    # draws npcs
    for i in range(len(npcs)):
        npc = npcs[i]

        # load image of first npc
        if i == 0:
            # pygame.draw.circle(screen, RED, npc[0], PLAYER_RADIUS, 0)

            npc1_rect = npc1.get_rect(center=npc[0])
            screen.blit(npc1, npc1_rect)

        # load image of second npc
        # only appears when within 3 tile radius of player

        elif i == 1:
            if dist(player_pos, npc[0]) < TILE_SIZE * 3:
                # if second npc enters field of vision, play random alert sound
                if not npc_near:
                    alert = choice([sound1, sound2, sound3])
                    alert.play()
                npc_near = True
                # pygame.draw.circle(screen, BLACK, npc[0], PLAYER_RADIUS, 0)
                npc2_rect = npc2.get_rect(center=npc[0])
                screen.blit(npc2, npc2_rect)

            else:
                npc_near = False

    # check for win, then play victory sound and exit game
    # show player time to win
    if check_win(player_pos):
        end_time = time.time()
        print(f'finished in {round(end_time - start_time)} seconds')
        win.play()
        time.sleep(12)

        running = False

    # check for loss, then play game over sound and exit game
    if visible:
        if any([game_over(player_pos, npc[0]) for npc in npcs]):
            print(':(')
            gameover.play()

            time.sleep(3)
            running = False

    # update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
