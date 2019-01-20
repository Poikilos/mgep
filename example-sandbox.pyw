#!/usr/bin/env python
import os
import sys
import pygame as pg

try:
    from mgep import *
except ImportError:
    print("missing mgep.")
    # print("try the following in git shell from projects directory:")
    # print("git clone https://github.com/poikilos/mgep")
    # print("then copy mgep/mgep to each specific project folder")
    print("Try the following in Command line")
    print(" (after installing Python 3 with"
          " 'Add Python to PATH' option:")
    print("pip install https://github.com/poikilos/mgep/zipball/master")
    exit(1)

pg.init()
screen = pg.display.set_mode(
    (1000, 700),
    pg.HWSURFACE | pg.DOUBLEBUF | pg.RESIZABLE
)
# set_scale(2)
# screen = pg.display.set_mode((720, 400),pg.FULLSCREEN)
# screen = pg.display.set_mode((640, 480),pg.FULLSCREEN)
clock = pg.time.Clock()
done = False
# load_tileset("tiny-16-basic/basictiles.png", 8, 15)
# load_material("grass", 9, 1)
# load_material("grass", 9, 2)
# load_material("dirt", 10, 1)
load_tileset(
    'mgep/collections/misc/underworld_load-outdoor-32x32.png',
    8,
    8
)
load_material('bedrock', 7, 2, native=False)
load_material('dirt', 1, 2)
load_material('grass', 1, 3)
load_material('grass', 2, 3)
load_material('grass', 3, 3)
load_material('sand', 1, 4)
# load_tileset("mgep/tiles/Atlas/terrain_atlas.png", 32, 32)
# load_material('bedrock', 14, 10, native=False)
# load_material('bedrock', 16, 6, native=False)
# load_material('dirt', 17, 4)
# load_material('grass', 23, 4)
# load_material('grass', 23, 6)
# load_material('grass', 22, 6)
# load_material('grass', 24, 6)
# load_material('stone', 26, 12)

load_tileset('mgep/sprites/Hyptosis/people.png', 4, 8)
load_character_3x4('male', 1, 1)
load_character_3x4('female', 1, 5)
# load_tileset(
#     'mgep/collections/misc/underworld_load-atlas-32x32.png',
#     16,
#     16
# )

world = load_world('world1', generate=True)
player_name = 'Steamy'
npc_name = 'Stella'
place_character('male', player_name, (0, 0))
place_character('female', npc_name, (2, 0))

def long_jump(e):
    move_direction(player_name, e['direction'])
    unit_jump(player_name, 5)

set_visual_debug(True)

# bind('draw_ui', on_draw_ui)
bind('swipe_direction', long_jump)
resize_count = 0
while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_DELETE:
                key = get_target_node_key()
                item = pop_node(key)
                if item is not None:
                    push_unit_item(player_name, item)
                else:
                    show_popup("You can't dig any deeper")
            elif event.key == pg.K_INSERT:
                # or event.key == pg.K_PAGEDOWN:
                item = pop_unit_item(player_name)
                if item is not None:
                    a = get_target_node_key()
                    stack = get_stack(a)
                    if stack is not None:
                        stack.append(item)
                else:
                    show_popup("You don't have any item selected")
            elif event.key == pg.K_SPACE:
                if not unit_jump(player_name, 5):
                    show_popup("cannot jump while airborne")
            elif event.key == pg.K_ESCAPE:
                done = True
            else:
                default_keydown(event)
        elif event.type == pg.KEYUP:
            stop_unit(player_name)
        elif event.type == pg.VIDEORESIZE:
            screen = pg.display.set_mode(
                event.size,
                pg.HWSURFACE | pg.DOUBLEBUF | pg.RESIZABLE
            )
            resize_count += 1
            print("resized to " + str(event.size) +
                  " {resize_count:" + str(resize_count) + "}")
        elif event.type == pg.MOUSEBUTTONDOWN:
            default_down(event)
            pass
        elif event.type == pg.MOUSEBUTTONUP:
            default_up(event)
            pass
        elif event.type == pg.MOUSEMOTION:
            default_motion(event)
            pass

    pressed = pg.key.get_pressed()
    # unit = units[player_name]
    # materials[unit['what']]['tmp']['sprites'][unit['pose']].advance()

    if pressed[pg.K_w]:
        move_y(player_name, 1)
    elif pressed[pg.K_s]:
        move_y(player_name, -1)
    if pressed[pg.K_a]:
        move_x(player_name, -1)
    elif pressed[pg.K_d]:
        move_x(player_name, 1)

    move_camera_to(player_name)
    draw_frame(screen)
    pg.display.flip()
    clock.tick(200)

save(player_name, get_unit(player_name))
save_world()
