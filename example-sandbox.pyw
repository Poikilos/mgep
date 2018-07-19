#!/usr/bin/env python
import os, sys
import pygame as pg
#region import pathing
# This import pathing nonsense is only needed because this py file is in
# the mgep directory. Place mgep directory inside your project's
# directory to avoid this issue.
mgep_name = "mgep"
if os.path.basename(os.path.dirname(os.path.abspath(__file__))) != "mgep":
    mgep_name = "mgep-master"
if os.path.basename(os.path.dirname(os.path.abspath(__file__))) == mgep_name:
    sys.path.insert(0, '..')
    print("in:"+os.getcwd())
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print("in:"+os.getcwd())
    #print("script in: "+os.path.basename(os.path.dirname(os.path.abspath(__file__))))
    import inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    print("file in:" + currentdir)
    parentdir = currentdir  # os.path.dirname(currentdir)
    print("parentdir:" + parentdir)
    sys.path.insert(0, parentdir)
if mgep_name == "mgep":
    try:
        from mgep import *
    except:
        print("missing mgep.")
        print("try the following in git shell from your project directory:")
        print("git clone https://github.com/poikilos/mgep")
        #print("sys.path: "+str(sys.path))
        #print("in: "+os.getcwd())
        exit(1)
else:
    print("ERROR: You must rename " + mgep_name + " to mgep")
    exit(1)
#endregion import pathing

pg.init()
screen = pg.display.set_mode((400, 300), pg.HWSURFACE | pg.DOUBLEBUF | pg.RESIZABLE)
#set_scale(2)
# screen = pg.display.set_mode((720, 400),pg.FULLSCREEN)
# screen = pg.display.set_mode((640, 480),pg.FULLSCREEN)
clock = pg.time.Clock()
done = False

#load_tileset("tiny-16-basic/basictiles.png", 8, 15)
#add_material("grass", 9, 1)
#add_material("grass", 9, 2)
#add_material("dirt", 10, 1)
load_tileset('mgep/collections/misc/underworld_load-outdoor-32x32.png', 8, 8)
load_material('bedrock', 7, 2, native=False)
load_material('dirt', 1, 2)
load_material('grass', 1, 3)
load_material('grass', 2, 3)
load_material('grass', 3, 3)
#load_tileset("mgep/tiles/Atlas/terrain_atlas.png", 32, 32)
#load_material('bedrock', 14, 10, native=False)
#load_material('bedrock', 16, 6, native=False)
#load_material('dirt', 17, 4)
#load_material('grass', 23, 4)
#load_material('grass', 23, 6)
#load_material('grass', 22, 6)
#load_material('grass', 24, 6)
#load_material('stone', 26, 12)


load_tileset('mgep/sprites/Hyptosis/people.png', 4, 8)
load_character_3x4('Steamy', 1, 1)
# load_tileset('mgep/collections/misc/underworld_load-atlas-32x32.png', 16, 16)

world = load_world('world1', generate=True)

place_character('Steamy', 'me', (0,0))

set_unit_value('me', 'items', [])
resize_count = 0
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
            elif event.key == pg.K_INSERT:
                if len(items) > 0:
                    a = get_selected_node_key()
                    blocks = get_blocks(a)
                    #if blocks is not None:
                    items = get_unit_value('me', 'items')
                    item = items[-1]
                    del items[-1]
                    blocks.append(item)
            elif event.key == pg.K_ESCAPE:
                done = True
        elif event.type == pg.KEYUP:
            stop_unit('me')
        elif event.type == pg.VIDEORESIZE:
            screen = pg.display.set_mode(event.size, pg.HWSURFACE | pg.DOUBLEBUF | pg.RESIZABLE)
            resize_count += 1
            print("resized to " + str(event.size) + \
                  " {resize_count:" + str(resize_count) + "}")

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
