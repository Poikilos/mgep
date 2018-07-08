#!/usr/bin/env python
import os, sys
import pygame as pg
from mgep import *

pg.init()
screen = pg.display.set_mode((400, 300))
set_scale(2)
# screen = pg.display.set_mode((720, 400),pg.FULLSCREEN)
# screen = pg.display.set_mode((640, 480),pg.FULLSCREEN)
clock = pg.time.Clock()
done = False

#load_tileset("tiny-16-basic/basictiles.png", 8, 15)
#add_material("grass", 9, 1)
#add_material("grass", 9, 2)
#add_material("dirt", 10, 1)
#load_tileset('mgep/collections/misc/underworld_load-outdoor-32x32.png', 8, 8)
#load_material('dirt', 1, 2)
#load_material('grass', 1, 3)
load_tileset("mgep/tiles/Atlas/terrain_atlas.png", 32, 32)
#load_material('bedrock', 14, 10, native=False)
load_material('bedrock', 16, 6, native=False)
load_material('dirt', 17, 4)
load_material('grass', 23, 4)
load_material('grass', 23, 6)
load_material('grass', 22, 6)
#load_material('grass', 24, 6)
load_material('stone', 26, 12)


load_tileset('mgep/sprites/Hyptosis/people.png', 4, 8)
load_character_3x4('Steamy', 1, 1)
# load_tileset('mgep/collections/misc/underworld_load-atlas-32x32.png', 16, 16)

world = load_world('world1', generate=True)

place_character('Steamy', 'me', (0,0))

set_unit_value('me', 'items', [])

while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                items = get_unit_value('me', 'items')
                a = get_selected_node_key()
                item = pop_node(a)
                if item is not None:
                    items.append(item)
                    print("You have " + str(get_whats(get_unit_value('me', 'items'))))
                else:
                    print("You can't dig any deeper")
            elif event.key == pg.K_ESCAPE:
                done = True
        elif event.type == pg.KEYUP:
            stop_unit('me')

    pressed = pg.key.get_pressed()
    # unit = units['me']
    # materials[unit['what']]['tmp']['sprites'][unit['pose']].advance()

    if pressed[pg.K_w]:
        move_y('me', 1)
    elif pressed[pg.K_s]:
        move_y('me', -1)
    elif pressed[pg.K_a]:
        move_x('me', -1)
    elif pressed[pg.K_d]:
        move_x('me', 1)

    move_camera_to('me')
    screen.fill((0, 0, 0))
    draw_frame(screen)
    pg.display.flip()
    clock.tick(60)
