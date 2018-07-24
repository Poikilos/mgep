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
    sys.path.append(parentdir)  # insert(0, parentdir)
if mgep_name == "mgep":
    try:
        from mgep import *
    except ImportError:
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
screen = pg.display.set_mode((1000, 700), pg.HWSURFACE | pg.DOUBLEBUF | pg.RESIZABLE)
#set_scale(2)
# screen = pg.display.set_mode((720, 400),pg.FULLSCREEN)
# screen = pg.display.set_mode((640, 480),pg.FULLSCREEN)
clock = pg.time.Clock()
set_visual_debug(True)
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
load_character_3x4('male', 1, 1)
load_character_3x4('female', 1, 5)
# load_tileset('mgep/collections/misc/underworld_load-atlas-32x32.png', 16, 16)

world = load_world('world1', generate=True)
player_name = 'Steamy'
npc_name = 'Stella'
place_character('male', player_name, (0,0))
place_character('female', npc_name, (2,0))

items = load(player_name, default=[])
set_unit_value(player_name, 'items', items)


def on_draw_ui(e):
    surf = e.get('screen')
    if surf is not None:
        size = surf.get_size()
        tile_size = get_tile_size()
        preview_size = int(tile_size[0]/2), int(tile_size[1]/2)
        outline_px = 1
        margin_px = 1
        square_size = (preview_size[0]+outline_px*2,
                       preview_size[1]+outline_px*2)
        x = margin_px + outline_px
        y = size[1] - preview_size[1] - (margin_px - outline_px) -1
        color = (64, 64, 64)
        counts = {}
        for item in items:
            what = item['what']
            if what not in counts:
                counts[what] = 0
            counts[what] += 1
        for what, count in counts.items():
            mat_surf = None
            #pose = item.get('pose')
            anim = get_anim_from_mat_name(what)  # , pose=pose)
            mat_surf = anim.get_surface()
            if mat_surf is None:
                continue
            pg.draw.rect(screen, color, pg.Rect(x-outline_px,
                                                y-outline_px,
                                                square_size[0],
                                                square_size[1]))
            surf.blit(pg.transform.scale(mat_surf,
                                         (preview_size[0],
                                          preview_size[1])),
                      (x,y))
            draw_text_vec2(str(count), (255,255,255), surf, (x+1, y+1))
            x += square_size[0] + margin_px

bind('draw_ui', on_draw_ui)
resize_count = 0
while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                items = get_unit_value(player_name, 'items')
                a = get_selected_node_key()
                item = pop_node(a)
                if item is not None:
                    items.append(item)
                    show_popup("You have " + str(get_whats(get_unit_value(player_name, 'items'))))
                else:
                    show_popup("You can't dig any deeper")
            elif event.key == pg.K_INSERT:  # or event.key == pg.K_PAGEDOWN:
                items = get_unit_value(player_name, 'items')
                if len(items) > 0:
                    a = get_selected_node_key()
                    blocks = get_blocks(a)
                    #if blocks is not None:
                    item = items[-1]
                    del items[-1]
                    blocks.append(item)
                else:
                    show_popup("You don't have any items")
            elif event.key == pg.K_ESCAPE:
                done = True
            elif event.key == pg.K_F3:
                toggle_visual_debug()
        elif event.type == pg.KEYUP:
            stop_unit(player_name)
        elif event.type == pg.VIDEORESIZE:
            screen = pg.display.set_mode(event.size, pg.HWSURFACE | pg.DOUBLEBUF | pg.RESIZABLE)
            resize_count += 1
            print("resized to " + str(event.size) + \
                  " {resize_count:" + str(resize_count) + "}")

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

save(player_name, items)
save_world()
