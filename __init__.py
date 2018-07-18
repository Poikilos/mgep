#!/usr/bin/env python
try:
    import pygame as pg
except:
    print("You must install pygame:")
    print("dnf install -y python3-pygame")
    exit(1)

import random
import math
# the world is a dict of lists (multiple gobs can be on one location)
block_thickness_as_y = 1
tilesets = {}
file_surfaces = {}
materials = {}
material_choose = [None]
world = {}
world["blocks"] = {}
#screen = None
player_unit_name = None
world_tile_size = None
units = {}
default_font = None
popup_text = ""
popup_showing_text = None
popup_surf = None
popup_shadow_surf = None
popup_sec = 0
popup_alpha = 0
visual_debug_enable = False
settings = {}
settings["popup_sec_per_character"] = .04
settings["popup_alpha_per_sec"] = 128.0
settings['text_antialiasing'] = True
temp_screen = None
text_pos = [0, 0]

last_loaded_path = None
# material spec:
# path: each material belongs to a tileset (saved as path string)
# serials: dict of tuple lists (coordinates of block in tileset). pose
#   subkey can be generated, but could also be special such as tr.grass
#   Coordinates are address as (x,y) by block (not pixel) starting at 1.
#   for top right of material such as mud where merges with grass,
#   or tr if material has alpha allowing merge with anything under it.
#   each item in the dict is a tile in the tileset.
#   serials[pose] is ALWAYS a list()
#
# world spec:
# * world is a dict where key is a location such as '0,0' and value
#   is a list.
#   * each list contains nodes
#     * each node is a dict with 'what' and 'pose' strings
#       where node['what'] is a material key and node['pose'] is a key
#       for the material[node['what']]['tmp']['sprites'] dictionary.

#class Camera():
#    
#    def __init__(self):
#        self.pos = (0,0)
#    
#    def move_to_character(self, name):
#        unit = units.get(name)
#        if unit is not None:
#            self.pos = unit.pos[0], unit.pos[1]
#        else:
#            raise ValueError("Cannot move since no character '" +
#                             name + "'")

camera = {}
camera['pos'] = (0, 0)
scale = None
desired_scale = None
def toggle_visual_debug():
    global visual_debug_enable
    if visual_debug_enable:
        set_visual_debug(False)
    else:
        set_visual_debug(True)

def set_visual_debug(boolean):
    global visual_debug_enable
    visual_debug_enable = boolean
    print("visual_debug_enable: " + str(visual_debug_enable))

def show_popup(s):
    global popup_text
    popup_text = s
    global popup_alpha
    popup_alpha = 255

def set_scale(whole_number):
    global scale
    global desired_scale
    scale = int(round(whole_number))
    desired_scale = scale

def get_key_at_pos(pos):
    w, h = world_tile_size  # tilesets[path]['tile_size']
    col = round(pos[0] / w)
    row = round(pos[1] / h)
    return str(col) + "," + str(row)

def get_selected_node_key():
    w, h = world_tile_size  # tilesets[path]['tile_size']
    #player_size = w, h  # TODO: get actual size
    pos = units[player_unit_name]['pos']
    #col = (pos[0] + player_size[0] / 2) / w
    #row = (pos[1] + player_size[1] / 2) / h
    col = round(pos[0] / w)
    row = round(pos[1] / h)
    return str(col) + "," + str(row)

def get_unit_value(name, what):
    return units[name][what]

def set_unit_value(name, what, v):
    units[name][what] = v

def move_x(name, amount):
    unit = units.get(name)
    if unit is not None:
        unit['pos'] = unit['pos'][0] + amount, unit['pos'][1]
        if amount > 0:
            pose = 'walk.right'
            unit['facing'] = 'right'
        elif amount < 0:
            pose = 'walk.left'
            unit['facing'] = 'left'
        if pose is not None:
            material = materials[unit['what']]
            if pose in material['tmp']['sprites']:
                reset_enable = False
                if pose != units[name]['pose']:
                    reset_enable = True
                units[name]['pose'] = pose
                if reset_enable:
                    material['tmp']['sprites'][pose].iter()
    else:
        raise ValueError("Cannot move since no unit '" +
                         name + "'")

def move_y(name, amount):
    unit = units.get(name)
    pose = None
    if unit is not None:
        unit['pos'] = unit['pos'][0], unit['pos'][1] + amount
        if amount > 0:
            pose = 'walk.up'
            unit['facing'] = 'up'
        elif amount < 0:
            pose = 'walk.down'
            unit['facing'] = 'down'
        if pose is not None:
            material = materials[unit['what']]
            if pose in material['tmp']['sprites']:
                unit['pose'] = pose
    else:
        raise ValueError("Cannot move since no unit '" + name + "'")
    

def move_camera_to(name):
    unit = units.get(name)
    if unit is not None:
        camera['pos'] = unit['pos'][0], unit['pos'][1]
    else:
        raise ValueError("Cannot move_camera_to since no unit '" +
                         name + "'")

# graphical object
#class Gob():
#    
#    def __init__(self):
#        self.pos = (0,0)

# Spritesheet class from https://www.pygame.org/wiki/Spritesheet
# changes by poikilos: file_surfaces cache
class SpriteSheet(object):
    def __init__(self, path):
        try:
            self.sheet = file_surfaces.get(path)
            if self.sheet is None:
                self.sheet = pg.image.load(path) #.convert_alpha()
                file_surfaces[path] = self.sheet
        except pg.error as message:
            print('Unable to load spritesheet image:', path)
            raise SystemExit(message)
    
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey=None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pg.Rect(rectangle)
        if colorkey is not None:
            image = pg.Surface(rect.size).convert()
        else:
            image = pg.Surface(rect.size, flags=pg.SRCALPHA) #.convert_alpha()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pg.RLEACCEL)
        return image
    
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey=None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
    
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey=None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey) 


# SpriteStripAnim class from https://www.pygame.org/wiki/Spritesheet
# except:
# * renamed frames to delay_count
# * boundary checking for delay_count
# * added order (uses oi to go out of order); frame indices start at 1
class SpriteStripAnim(object):
    """sprite strip animator
    
    This class provides an iterator (iter() and next() methods), and a
    __add__() method for joining strips which comes in handy when a
    strip wraps to the next row.
    order: a list of indices (starting at 1) in case frames should be
           used out of order
    """
    def __init__(self, path, rect, count, colorkey=None, loop=False, delay_count=1, order=None):
        """construct a SpriteStripAnim
        
        path, rect, count, and colorkey are the same arguments used
        by spritesheet.load_strip.
        
        loop is a boolean that, when True, causes the next() method to
        loop. If False, the terminal case raises StopIteration.
        
        delay_count is the count to return the same image
        before iterator advances to the next image.
        """
        self.path = path
        ss = SpriteSheet(path)
        self.images = ss.load_strip(rect, count, colorkey)
        self.image = None
        self.i = 0  # current frame index
        self.oi = 0  # current index in the custom order
        self.order = order
        if order is not None:
            self._go_to_order()
        self.image = self.images[self.i]
        self.loop = loop
        
        self.delay_count = int(delay_count)
        if self.delay_count<1:
            print("WARNING: setting delay_count to 1 " +
                  "since was " + str(self.delay_count))
            self.delay_count = 1
        self.f = delay_count

    def iter(self):
        self.i = 0
        self.oi = 0
        if self.order is not None: self._go_to_order()
        self.f = self.delay_count
        return self

    def get_surface(self):
        # return self.images[self.i]
        return self.image

    def _go_to_order(self):
        if self.order is not None:
            if self.oi >= len(self.order):
                msg = "self.oi was " + str(self.oi)
                print("WARNING in _go_to_order: " + msg)
                #raise ValueError(msg)
                self.oi = 0
            new_i = self.order[self.oi] - 1  # -1 since starts at 1
            if new_i >= 0 and new_i < len(self.images):
                self.i = new_i
                # do NOT set self.image = self.images[self.i] here since
                # using iterator logic (see __next__) which increments only
            else:
                raise ValueError("Bad order index (should start at 1) " +
                                 str(new_i))
        else:
            raise RuntimeError("Cannot _go_to_order with no order.")

    def advance(self):
        if self.order is not None:
            if self.oi >= len(self.order):
                if not self.loop:
                    raise StopIteration
                else:
                    self.oi = 0
            self._go_to_order()
        else:
            if self.i >= len(self.images):
                if not self.loop:
                    raise StopIteration
                else:
                    self.i = 0
        self.image = self.images[self.i]
        self.f -= 1
        if self.f == 0:
            if self.order is not None:
                self.oi += 1
            else:
                self.i += 1
            self.f = self.delay_count

    def __next__(self):
        self.advance()
        return self.image

    def __add__(self, ss):
        self.images.extend(ss.images)
        return self


#def set_screen(s):
#    global screen
#    screen = s

#def init():
#    global settings
#    if settings is None:

prev_frame_ticks = None
min_fps_ticks = 1000
total_ticks = 0
frame_count = 0
fps_s = "?"
scalable_surf = None
scalable_surf_scale = None

#region reinitialized each frame
win_size = None
scaled_size = None
scaled_block_size = None
block_half_counts = None
start_loc = None
end_loc = None
#endregion reinitialized each frame

def draw_frame(screen):
    global settings
    global temp_screen
    global text_pos
    global win_size
    global scaled_size
    global scaled_block_size
    global block_half_counts
    global start_loc
    global end_loc
    global block_thickness_as_y
    global scale
    global desired_scale
    global scalable_surf
    global scalable_surf_scale
    text_pos = [4,4]
    # pg.draw.rect(screen, color, pg.Rect(x, y, 64, 64))
    new_win_size = screen.get_size()
    if win_size is None or win_size[0] != new_win_size[0] or win_size[1] != new_win_size[1]:
        win_size = screen.get_size()
        scale = None
        scalable_surf = None
        #print("Changed window size...")
        #print("win_size: " + str(win_size))
        #print("scale: " + str(scale))
    # an ideal scale will have about 12 meters for smallest dimension
    short_px_count = win_size[1]
    if win_size[0] < win_size[1]:
        short_px_count = win_size[0]
    ideal_tile_h = short_px_count / 12
    if scale is None:
        if desired_scale is None:
            scale = int(round(ideal_tile_h/world_tile_size[1]))
            print("scale automatically chosen: " + str(scale))
        else:
            scale = desired_scale
    scaled_size = win_size[0] / scale, win_size[1] / scale
    if scalable_surf is None or scale != scalable_surf_scale:
        scalable_surf = pg.Surface((int(scaled_size[0]), int(scaled_size[1]))).convert()  # , flags=pg.SRCALPHA)
        scalable_surf_scale = scale
        temp_screen = scalable_surf

    camera_loc = get_loc_at_px(camera['pos'])
    scaled_block_size = world_tile_size[0] * scale, world_tile_size[1] * scale
    block_counts = math.ceil(scaled_size[0] / world_tile_size[0]), math.ceil(scaled_size[1] / world_tile_size[1])
    block_half_counts = int(block_counts[0] / 2) + 1, int(block_counts[1] / 2) + 1
    # reverse the y order so larger depth value is drawn below other layers
    # (end_loc's y is NEGATIVE on purpose due to draw order)
    max_stack_preload_count = 5
    extra_count = max_stack_preload_count * block_thickness_as_y
    start_loc = camera_loc[0] - block_half_counts[0], camera_loc[1] + block_half_counts[1]
    end_loc = (camera_loc[0] + block_half_counts[0],
               camera_loc[1] - block_half_counts[1] - extra_count)
    screen_half = scaled_size[0] / 2, scaled_size[1] / 2
    w, h = world_tile_size
    blocks = world["blocks"]
    # for k, v in blocks.items():
    block_y = start_loc[1]
    while block_y >= end_loc[1]:
        block_x = start_loc[0]
        while block_x <= end_loc[0]:
            k = str(block_x) + "," + str(block_y)
            v = blocks.get(k)
            if v is not None:
                cs = k.split(",")
                sk = k  # spatial key
                col, row = (int(cs[0]), int(cs[1]))
                offset = 0
                for i in range(len(v)):
                    node = v[i]
                    name = k + "[" + str(i) + "]"  # such as '0,0[1]'
                    pos = (col*w, row*h)
                    pose = None
                    pose = node.get('pose')
                    if pose is None:
                        # print("WARNING: no pose for " + node['what'] + " at " + k)
                        pose = materials[node['what']].get('default_pose')
                        if pose is None:
                            print("WARNING: no default_pose for " + node['what'])
                            pose = random.choice(list(material['tmp']['sprites']))
                    anim = materials[node['what']]['tmp']['sprites'][pose]
                    src_size = anim.get_surface().get_size()
                    x = pos[0]-camera['pos'][0] + screen_half[0] - src_size[0]/2
                    # if x+w < 0 or x >= win_size[0]:
                    #     continue
                    y = -1*(pos[1]-camera['pos'][1]) + screen_half[1] - src_size[1]/2
                    # if y+w < 0 or y >= win_size[0]:
                    #     continue
                    # if k=="me":
                    #     print("me at " + str((x,y)))
                    scalable_surf.blit(anim.get_surface(), (x,y-offset))
                    animate = node.get('animate')
                    if animate is True:
                        anim.advance()
                    offset += block_thickness_as_y
            block_x += 1
        block_y -= 1
    for k, v in units.items():  # TODO: check for python2 units.iteritems()
        material = materials[v['what']]
        anim = material['tmp']['sprites'][v['pose']]
        if v['animate']:
            anim.advance()
            # if v['pose'] != 0: print("iter " + v['pose'])
        # else:
            # if v['pose'] != 0: print("hold " + v['pose'])
        screen_half = scaled_size[0] / 2, scaled_size[1] / 2
        w, h = world_tile_size
        # center_tile_tl_pos = win_size[0]/2-world_tile_size[0]/2,
        #                      win_size[1]/2-world_tile_size[1]/2
        # center_tile_tl_pos = (0,0)
        pos = v['pos']
        sk = get_key_at_pos(pos)
        offset = -1
        stack = blocks.get(sk)
        if stack is not None:
            offset = len(stack)
        src_size = anim.get_surface().get_size()
        x = (pos[0] - camera['pos'][0]) + screen_half[0] - src_size[0]/2
        # if x+w < 0 or x >= win_size[0]:
        #     continue
        y = -1*(pos[1] - camera['pos'][1]) + screen_half[1] - src_size[1]/2
        # if y+w < 0 or y >= win_size[0]:
        #     continue
        # if k=="me":
        #     print("me at " + str((x,y)))
        scalable_surf.blit(anim.get_surface(), (x,y-offset))
        # surface = next(anim)
    global default_font

    global popup_showing_text
    if default_font is None:
        default_font = pg.font.SysFont('Arial', 12)
    global popup_surf
    global popup_shadow_surf
    global popup_text
    global popup_alpha
    global popup_sec

    global prev_frame_ticks
    global total_ticks
    global frame_count
    global visual_debug_enable
    passed = 0.0  # seconds
    passed_ms = 0
    this_frame_ticks = pg.time.get_ticks() 
    fps = 0.0  # clock.get_fps()
    global fps_s
    if prev_frame_ticks is not None:
        passed_ms = this_frame_ticks - prev_frame_ticks
        prev_frame_ticks = this_frame_ticks
        passed = float(passed_ms) / 1000.0
        total_ticks += passed_ms
        frame_count += 1
        if total_ticks >= min_fps_ticks:
            #avg = float(total_ticks) / float(min_fps_ticks)
            fps = frame_count / (float(total_ticks)/1000.0)
            fps_s = "{0:.1f}".format(round(fps,1))
        #if passed > 0.0:
            #fps = 1000/passed
            #fps_s = str(fps)
            # fps_s = str(clock.get_fps())  # clock is only in game
    else:
        prev_frame_ticks = this_frame_ticks

    if visual_debug_enable:
        push_text(fps_s)

    if (popup_surf is None) or (popup_showing_text != popup_text):
        if popup_text is not None:
            popup_surf = default_font.render(popup_text, settings['text_antialiasing'], (255, 255, 255))
            popup_shadow_surf = default_font.render(popup_text, False, (0, 0, 0))
            popup_sec = settings["popup_sec_per_character"] * len(popup_text)
            popup_alpha = 255
            settings["popup_sec_per_character"] = .04
        else:
            popup_surf = default_font.render("", settings['text_antialiasing'], (255, 255, 255))
            popup_shadow_surf = default_font.render("", settings['text_antialiasing'], (0, 0, 0))
        popup_showing_text = popup_text

    if popup_surf is not None:
        if popup_sec > 0:
            popup_sec -= passed
        if popup_alpha > 0:
            if popup_sec <= 0:
                popup_shadow_surf.set_alpha(popup_alpha)
                popup_surf.set_alpha(popup_alpha)
            scalable_surf.blit(popup_shadow_surf,(text_pos[0]+2,text_pos[1]+1))
            scalable_surf.blit(popup_surf,(text_pos[0],text_pos[1]))
            text_size = popup_surf.get_size()
            text_pos[1] += text_size[1]
            popup_alpha -= settings["popup_alpha_per_sec"] * passed
    screen.blit(pg.transform.scale(scalable_surf, (int(win_size[0]),int(win_size[1]))),(0,0))
    show_stats_once()

show_stats_enable = True
def show_stats_once():
    global show_stats_enable
    if show_stats_enable:
        print()
        print("win_size: " + str(win_size))
        print("scaled_size: " + str(scaled_size))
        print("scaled_block_size: " + str(scaled_block_size))
        print("block_half_counts: " + str(block_half_counts))
        print("start_loc: " + str(start_loc))
        print("end_loc: " + str(end_loc))
        print("scale: " + str(scale))
    show_stats_enable = False


def push_text(s, color=(255,255,255), screen=None):
    global text_pos
    global temp_screen
    global settings
    if screen is not None:
        temp_screen = screen
    if temp_screen is not None:
        s_surf = default_font.render(s, settings['text_antialiasing'], color)
        text_size = s_surf.get_size()
        temp_screen.blit(s_surf, (text_pos[0],text_pos[1]))
        text_pos[1] += text_size[1]

# series: if more than one frame, you can pass pre-generated sprite loop 
# order: (requires len(series)>1) indices of frames specifying order
# starting at 1 
def _load_sprite(what, cells, order=None, gettable=True,
                     pose=None, path=None, has_ai=False,
                     native=True, overlayable=False,
                     biome="default", series=None, loop=True,
                     default_animate=None):
    #results = {}
    if path is None:
        path = last_loaded_path
    material = None
    material = materials.get(what, None)  # default to new material
    if material is None:
        material = {}
        material['tmp'] = {}
        materials[what] = material
    if pose is None:
        try_as_i = 0
        try_as = str(try_as_i)
        mfr=material.get("serials")
        if mfr is not None:
            while try_as in mfr:
                try_as_i += 1
                try_as = str(try_as_i)
        else:
            material["serials"] = {}
        pose = try_as
    else:
        if material.get("serials") is None:
            material['serials'] = {}
    prev_cells = material["serials"].get(pose)
    if prev_cells is None:
        material["serials"][pose] = cells
    else:
        material["serials"][pose].extend(cells)

    #prev_sprite = material['tmp']['sprites'].get(pose)
    w, h = tilesets[path]['tile_size']
    if series is None:
        for col, row in cells:
            rect = ((col-1)*w, (row-1)*h, w, h)
            if series is None:
                series = SpriteStripAnim(path, rect, 1, loop=loop, delay_count=20)
            else:
                series += SpriteStripAnim(path, rect, 1, loop=loop, delay_count=20)

    if material['tmp'].get('sprites') is None:
        material['tmp']['sprites'] = {}

    if material['tmp']['sprites'].get(pose) is None:
        material['tmp']['sprites'][pose] = series
    else:
        material['tmp']['sprites'][pose] += series

    if material.get('default_pose') is None:
        material['default_pose'] = pose
    material["overlayable"] = overlayable
    material["biome"] = biome
    surf = file_surfaces.get(path)
    if surf is None:
        surf = pg.image.load(path) #.convert_alpha()
        file_surfaces[path] = surf
    #w, h = surf.get_size()
    #return results

# gettable allows player to get material
# path: if None, then uses last loaded tileset
def load_material(what, column, row, gettable=True,
                 pose=None, path=None, has_ai=False,
                 native=True, overlayable=False,
                 biome="default", count=1, order=None,
                 next_offset="right", loop=True, default_animate=None):
    global world_tile_size
    if default_animate is None:
        if count > 1:
            default_animate = True
    if path is None: path = last_loaded_path
    cells = []
    next_offset = next_offset.lower()
    for i in range(count):
        if next_offset=="up":
            cells.append((row-i, column))
        elif next_offset=="down":
            cells.append((row+i, column))
        elif next_offset=="left":
            cells.append((row, column-i))
        elif next_offset=="right":
            cells.append((row, column+i))
        else:
            print("ERROR in load_material: unknown next_offset " +
                  str(next_offset) + " (use 'up' 'down' 'left' 'right'")
            cells.append((row+i, column))
    if native:
        material_choose.append(what)  # increase spawn odds each time
    if order is not None:
        for n in order:
            if n > count:
                count = n  # n is a counting number (starts at 1)
    w, h = tilesets[path]['tile_size']
    col = column
    rect = ((col-1)*w, (row-1)*h, w, h)
    series = SpriteStripAnim(path, rect, count, order=order, loop=loop, delay_count=20)
    _load_sprite(what, cells, order=order, gettable=gettable,
                 pose=pose, path=path, has_ai=has_ai,
                 native=native,
                 overlayable=overlayable,
                 biome=biome, series=series, loop=loop,
                 default_animate=default_animate)
    if what not in materials:
        materials[what] = {}
    prev_path = materials[what].get('path')
    if prev_path is not None:
        if prev_path != path:
            print("ERROR: material " + what + " is trying to load a" +
                  " tile from '" + path + "' but was created using " +
                  "'" + prev_path + "'")
            materials[what]['path'] = path
    else:
        materials[what]['path'] = path
    if world_tile_size is None:
        world_tile_size = tilesets[path]['tile_size']
        print("world_tile_size from material: " + str(world_tile_size))

#   same as load_material but with different defaults
def load_character(what, column, row, gettable=False,
                  pose=None, path=None, has_ai=False,
                  native=False, overlayable=True,
                  biome=None, count=1, order=None,
                  next_offset="right"):
    load_material(what, column, row, gettable=gettable,
                 pose=pose, path=path, has_ai=has_ai,
                 native=native,
                 overlayable=overlayable,
                 biome=biome, count=count, order=order,
                 next_offset=next_offset, loop=True,
                 default_animate=True)

# loads a "3x4" character sheet where columns
# are in standard 3-frame order:
# [idle,step1,step3] (where idle frame is also step2)
# and the rows are arranged based on Liberated Pixel Cup:
# ['walk.up','walk.left','walk.down','walk.right'] 
def load_character_3x4(what, column, row):
    load_character(what, column, row, pose='idle.up')
    load_character(what, column, row+1, pose='idle.left')
    load_character(what, column, row+2, pose='idle.down')
    load_character(what, column, row+3, pose='idle.right')
    load_character(what, column, row, order=[2,1,3,1], pose='walk.up')
    load_character(what, column, row+1, order=[2,1,3,1], pose='walk.left')
    load_character(what, column, row+2, order=[2,1,3,1], pose='walk.down')
    load_character(what, column, row+3, order=[2,1,3,1], pose='walk.right')

def _place_unit(what, name, pos, pose=None, animate=True):
    if name in units:
        raise ValueError("There is already a unit named " + name)
    units[name] = {}
    units[name]['what'] = what
    units[name]['pos'] = pos[0], pos[1]
    try:
        if pose is None: pose = materials[what]['default_pose']
    except TypeError:
        raise TypeError("ERROR in _place_unit: what is '" + \
                        str(what) + "' is unknown unit type")
    units[name]['pose'] = pose
    units[name]['animate'] = animate
    units[name]['facing'] = 'up'

def stop_unit(name):
    unit = units[name]
    material = materials[unit['what']]
    direction = unit.get('facing')
    pose = 'idle'
    if direction is not None:
        pose = 'idle.' + direction
    if pose in material['tmp']['sprites']:
        unit['pose'] = pose
    else:
        unit['animate'] = False

# creates a new unit based on 'what' graphic, with a unique name
# pos: the (x,y) cartesian (y up) position of the character
def place_character(what, name, pos):
    _place_unit(what, name, pos)
    global player_unit_name
    if player_unit_name is None:
        player_unit_name = name

def load_tileset(path, count_x, count_y, margin_l=0, margin_t=0,
                 margin_r=0, margin_b=0, spacing_x=0, spacing_y=0):
    global last_loaded_path
    last_loaded_path = path
    surf = file_surfaces.get(path)
    if surf is None:
        surf = pg.image.load(path) #s.convert_alpha()
        file_surfaces[path] = surf
    w, h = surf.get_size()
    tilesets[path] = {}
    u_size = w-margin_l-margin_r+spacing_x, h-margin_t-margin_b+spacing_y
    f_s = u_size[0]/count_x-spacing_x, u_size[1]/count_y-spacing_y
    tilesets[path]['tile_size'] = int(f_s[0]), int(f_s[1])
    t_s = tilesets[path]['tile_size']
    if t_s[0] != int(f_s[0]) or t_s[1] != int(f_s[1]) or \
            t_s[0] < 1 or t_s[1] < 1:
        raise ValueError("tileset geometry is nonsensical: derived "
              "tile size " + str(f_s) + " should be whole number > 0")

#def setup_game(set_materials, tile_size=32):
#    global materials
#    materials = set_materials
#
#    if os.path.isfile("world.json"):
#        pass

def get_loc_at_px(pos):
    world_loc = int(pos[0] / world_tile_size[0]), int(pos[1] / world_tile_size[1])
    return world_loc

def get_gobs_at(loc):
    result = None
    # sk for spatial key
    sk = str(loc[0])+","+str(loc[1])
    raise NotImplementedError("NYI")
    return result    

def _place_world():
    if last_loaded_path is None:
        raise ValueError("missing last_loaded_path (must load_tileset"
                         "before load_world can call graphics methods)")
    #blocks = world["blocks"]
    #for k, v in blocks.items():
    #    cs = k.split(",")  # key is a location string
    #    col, row = (int(cs[0]), int(cs[1]))
    #    w, h = world_tile_size  # tilesets[path]['tile_size']
    #    for i in range(len(v)):
    #        node = v[i]
    #        name = k + "[" + str(i) + "]"
    #        pose = None
    #        if 'pose' in node:
    #            pose = node['pose']
    #        _place_unit(node['what'], name, (col*w, row*h), pose=pose)

def get_whats(nodes):
    results = []
    for node in nodes:
        what = node.get('what')
        results.append(what)
    return results

def pop_node(key):
    sk = key  # spatial key
    result = None
    blocks = world["blocks"]
    if sk in blocks:
        if len(blocks[sk]) > 1:
            result = blocks[sk][-1]
            del blocks[sk][-1]
            #result = units[sk]
            #units.remove(sk)
    else:
        print("ERROR in pop_unit: bad key " + str(key) + "(must be "
              "'int,int' where int are whole numbers and location "
              "is a loaded part of the world")
    return result

def load_world(name, generate=False):
    global world
    world = {}
    world["blocks"] = {}
    blocks = world["blocks"]
    #TODO: if generate:
    bedrock_what = None
    material_all = list(materials)
    if 'bedrock' in material_all:
        bedrock_what = 'bedrock'
    elif 'dirt' in material_all:
        bedrock_what = 'dirt'
    for col in range(-30, 30):
        for row in reversed(range(-30, 30)):
            sk = str(col)+","+str(row)
            blocks[sk] = []
            if len(materials) > 0:
                if bedrock_what is not None:
                    bedrock = {}  # recreate each time so not instance
                    bedrock['what'] = bedrock_what
                    if bedrock is not None: blocks[sk].append(bedrock)
                    else:
                        print("WARNING: no 'bedrock' material")
                node = {}
                node['what'] = random.choice(material_choose)
                if node['what'] is not None:
                    default_animate = \
                        materials[node['what']].get('default_animate')
                    if default_animate is True: 
                        node['animate'] = True
                    #else None or False so don't waste storage space
                    material = materials[node['what']]
                    # converting a dict to a list yields the keys:
                    node['pose'] = random.choice(list(material['tmp']['sprites']))
                    #print("generated " + node['what'] + " pose " + node['pose'] + " at " + sk)
                    blocks[sk].append(node)
                #else:
                    #print("generated None at " + sk)
    _place_world()

if __name__ == "__main__":
    print("Instead of running this file, use it in your program like:\n"
          "from mgep import *\n"
          "#see also example-*.pyw")
