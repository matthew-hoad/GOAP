import pygame
from PIL import Image
import random
import city
import objects
import time
import numpy as np
from math import floor
import asyncio


# GENERAL SETUP
WIDTH = 820
HEIGHT = 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

game_display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ant Farm")
clock = pygame.time.Clock()

# GETTING THE WORLD AND G - A DICT FOR DJIKSTRA
tile_norm = pygame.image.load('img/tile_norm.png')
tile_caf = pygame.image.load('img/tile_path.png')
tile_ws = pygame.image.load('img/tile_ws.png')
tile_bed = pygame.image.load('img/tile_bed.png')
ant_sprite = pygame.image.load('img/ant_sprite_red.png')
# game_display.blit(tile_norm, (x, y))
worldmap = Image.open('img/map.png')
tileWidth = int(WIDTH/float(worldmap.size[0]))
tileHeight = int(HEIGHT/float(worldmap.size[1]))

def draw_environment(world):
    game_display.fill(BLACK)
    paths, beds, workstations = world.tiles['paths'], world.tiles['beds'], world.tiles['workstations']
    for path in world.tiles['paths']:
        game_display.blit(tile_norm, (path.x*10, path.y*10))

    for ws in world.tiles['workstations']:
        game_display.blit(tile_ws, (ws.x*10, ws.y*10))

    for bed in world.tiles['beds']:
        game_display.blit(tile_bed, (bed.x*10, bed.y*10))

    for ant in world.ants:
        # print(ant.x, ant.y)
        game_display.blit(ant_sprite, (int(ant.x*10), int(ant.y*10)))

    pygame.display.update()

def initialise_map():
    paths = []
    beds = []
    workstations = []
    cafes = []
    walls = []
    worldmap = Image.open('img/map.png')
    mapimg = worldmap.load()
    tileIDstack = [str(i) for i in range(worldmap.size[0]*worldmap.size[1])]
    for j, y in enumerate(range(worldmap.size[1])):
        for i, x in enumerate(range(worldmap.size[0])):
            if mapimg[x, y] == (255, 0, 0):
                # print('Putting a cafe at ({}, {})'.format(x, y))
                kind = 'Cafe'
                new_tile = city.Tile(tileIDstack.pop(), x, y, kind, occupant=None, owner=None)
                cafes.append(new_tile)
            elif mapimg[x, y] == (0, 255, 0):
                # print('Putting a workstation at ({}, {})'.format(x, y))
                kind = 'Work Station'
                new_tile = city.Tile(tileIDstack.pop(), x, y, kind, occupant=None, owner=None)
                workstations.append(new_tile)
            elif mapimg[x, y] == (0, 0, 255):
                # print('Putting a bed at ({}, {})'.format(x, y))
                kind = 'Bed'
                new_tile = city.Tile(tileIDstack.pop(), x, y, kind, occupant=None, owner=None)
                beds.append(new_tile)
            elif mapimg[x, y] == (255, 255, 255):
                # print('Putting a path at ({}, {})'.format(x, y))
                kind = 'Path'
                new_tile = city.Tile(tileIDstack.pop(), x, y, kind, occupant=None, owner=None)
                paths.append(new_tile)
            else:
                # print('Putting a wall at ({}, {})'.format(x, y))
                kind = 'Wall'
                new_tile = city.Tile(tileIDstack.pop(), x, y, kind, occupant=None, owner=None)
                walls.append(new_tile)
            # time.sleep(0.2)
    # GENERATE ANT SEEDS
    seeds = []
    for a in range(10):
        for b in range(10):
            for c in range(10):
                seeds.append('{}{}{}'.format(a, b, c))
    seeds = seeds[:len(beds)]
    # SHUFFLE WORK STATIONS AND RECHARGE STATIONS
    random.shuffle(beds)
    random.shuffle(workstations)
    # GENERATE ANTS FROM SEEDS
    ants = []
    for seed, home, work in zip(seeds, beds, workstations):
        myAnt = objects.Ant(seed, home, work)
        home.owner = myAnt
        work.owner = myAnt
        myAnt.money = 100
        myAnt.energy = 10
        myAnt.set_state()
        myAnt.set_goals_and_actions()
        ants.append(myAnt)
    tiles = {'paths': paths, 'workstations': workstations, 'beds': beds, 'cafes': cafes}
    world = city.World(tiles, ants)
    for ant in world.ants:
        ant.world = world
    return world

async def make_ant_think(ant, sem):
    async with sem:
        ant.set_state()
        if ant.action == None:
            # print(ant.seed, 'goaping')
            ant.goap(ant.goals[0])
        ant.perform_action()
        return ant

async def process_ants(world):
    sem = asyncio.Semaphore(100, loop=loop)
    tasks = [make_ant_think(ant, sem) for ant in world.ants]
    ants = await asyncio.gather(*tasks)
    # for ant in world.ants:
    #     # print(world, ant.world)
    #     # print(ant.seed, ant.intelligence)
    #     ant.set_state()
    #     make_ant_think(ant)
    return ants

def main():
    world = initialise_map()
    minute = 1
    hour = 1
    day = 1
    month = 1
    year = 1
    while True:
        if minute == 60:
            minute = 1
            hour +=1
        if hour == 24:
            hour = 1
            day += 1
        if day == 30:
            day = 1
            month += 1
        if month == 12:
            month = 1
            year += 1
        # print('{}:{} of {}/{}/{}'.format(hour, minute, day, month, year))
        delta = clock.tick(3)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        # print(world.G['202'])
        loop.run_until_complete(process_ants(world))
        # print('\n\nDrawing environment for the {}th time\n\n'.format(count))
        draw_environment(world)
        # time.sleep(1)
        # print(len(ants))
        minute += 1
        if day == 2:
            # print('day 2')
            break


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    main()
    loop.close()
