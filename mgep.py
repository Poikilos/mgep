#!/usr/bin/env python
try:
    import pygame as pg
except:
    print("You must install pygame:")
    print("dnf install -y python3-pygame")
    exit(1)

import random

# the world is a dict of lists (multiple gobs can be on one location)

tilesets = {}
file_surfaces = {}
materials = {}
material_choose = []
world = {}
screen = None
player_sprite_name = None
world_tile_size = None

last_loaded_path = None
# material spec:
# path: each material belongs to a tileset (saved as path string)
# series: dict of tuples (coordinates of block in tileset). use_as
#   subkey can be generated, but could also be special such as tr.grass
#   Coordinates are address as (x,y) by block (not pixel) starting at 1.
#   for top right of material such as mud where merges with grass,
#   or tr if material has alpha allowing merge with anything under it.
#   each item in the dict is a tile in the tileset.
#   series[use_as] is ALWAYS a list()

import pygame

# Spritesheet class from https://www.pygame.org/wiki/Spritesheet
# changes by poikilos: file_surfaces cache
class SpriteSheet(object):
    def __init__(self, filename):
        try:
            self.sheet = file_surfaces.get(path)
            if self.sheet is None:
                self.sheet = pygame.image.load(filename).convert()
                file_surfaces[path] = self.sheet
        except pygame.error as message:
            print('Unable to load spritesheet image:', filename)
            raise SystemExit(message)
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey) 

# SpriteStripAnim class from https://www.pygame.org/wiki/Spritesheet
# except:
# * renamed frames to delay_count
# * added order (uses oi to go out of order)
class SpriteStripAnim(object):
    """sprite strip animator
    
    This class provides an iterator (iter() and next() methods), and a
    __add__() method for joining strips which comes in handy when a
    strip wraps to the next row.
    """
    def __init__(self, filename, rect, count, colorkey=None, loop=False, delay_count=1, order=None):
        """construct a SpriteStripAnim
        
        filename, rect, count, and colorkey are the same arguments used
        by spritesheet.load_strip.
        
        loop is a boolean that, when True, causes the next() method to
        loop. If False, the terminal case raises StopIteration.
        
        delay_count is the count to return the same image
        before iterator advances to the next image.
        """
        self.filename = filename
        ss = SpriteSheet(filename)
        self.images = ss.load_strip(rect, count, colorkey)
        self.i = 0  # current frame index
        self.oi = 0  # current index in the custom order
        self.order = order
        self.loop = loop
        
        self.delay_count = int(delay_count)
        elif self.delay_count<1:
            print("setting delay_count to 1 " +
                  "since was " + str(self.delay_count))
            self.delay_count = 1
        self.f = delay_count
    def iter(self):
        self.i = 0
        self.oi = 0
        self.f = self.delay_count
        return self

    def __next__(self):
        if (self.order is not None):
            #asdf finish this

        if self.i >= len(self.images):
            if not self.loop:
                raise StopIteration
            else:
                self.i = 0
        image = self.images[self.i]
        self.f -= 1
        if self.f == 0:
            self.i += 1
            self.f = self.delay_count
        return image

    def __add__(self, ss):
        self.images.extend(ss.images)
        return self

def set_screen(s):
    global screen
    screen = s

def _add_sprite(name, cells, order=None, gettable=True,
                     use_as=None, path=None, has_ai=False,
                     native=True, overlayable=False,
                     biome="default", series=None, loop=True):
    #results = {}
    if path is None:
        path = last_loaded_path
    material = None
    material = materials.get(name, None)  # default to new material
    if material is None:
        material = {}
        material['tmp'] = {}
        materials[name] = material
    if use_as is None:
        try_as_i = 0
        try_as = str(try_as_i)
        mfr=material.get("series")
        if mfr is not None:
            while try_as in mfr:
                try_as_i += 1
                try_as = str(try_as_i)
        else:
            material["series"] = {}
        use_as = try_as
    prev_cells = material["series"].get("use_as")
    if prev_cells is None:
        material["series"][use_as] = cells
    else:
        material["series"][use_as].extend(cells)
    prev_sprite = material['tmp']['series_sprite']
    w, h = tilesets[path]['tile_size']
    if series is None:
        for col, row in cells:
            rect = ((col-1)*w, (row-1)*h, w, h)
            if series is None:
                series = SpriteStripAnim(path, rect, 1, loop=loop)
            else:
                series += SpriteStripAnim(path, rect, 1, loop=loop)
    if prev_sprite is None:
        material['tmp']['series_sprite'] = series
    else:
        prev_sprite += series
    material["overlayable"] = overlayable
    material["biome"] = biome
    surf = file_surfaces.get(path)
    if surf is None:
        surf = pygame.image.load(filename).convert()
        file_surfaces[path] = surf
    #w, h = surf.get_size()
    #return results

# gettable allows player to get material
# path: if None, then uses last loaded tileset
def add_material(name, row, column, gettable=True,
                 use_as=None, path=None, has_ai=False,
                 native=True, overlayable=False,
                 biome="default", count=1, order=None,
                 next_offset="right", loop=True):
    if path is None: path = last_loaded_path
    cells = []
    next_offset = next_offset.lower()
    for i in range(count):
        if next_offset=="right":
            cells.append((row+i, column))
        elif next_offset=="down":
            cells.append((row, column+i))
        else:
            print("ERROR in add_material: unknown next_offset " +
                  str(next_offset) + " (must be 'right' or 'down'")
            cells.append((row+i, column))
    material_choose.append(name)  # increase spawn odds each time
    if order is not None:
        for n in order:
            if n > count:
                count = n  # n is a counting number (starts at 1)
    w, h = tilesets[path]['tile_size']
    col = column
    rect = ((col-1)*w, (row-1)*h, w, h)
    series = SpriteStripAnim(path, rect, count, loop=loop)
    _add_sprite(name, cells, order=order, gettable=gettable,
                 use_as=use_as, path=path, has_ai=has_ai,
                 native=native,
                 overlayable=overlayable,
                 biome=biome, series=series, loop=loop)
    if name not in materials:
        materials[name] = {}
    prev_path = materials[name].get('path')
    if prev_path is not None:
        if prev_path != path:
            print("ERROR: material " + name + " is trying to load a" +
                  " tile from '" + path + "' but was created using " +
                  "'" + prev_path + "'")
            materials[name]['path'] = path
    else:
        materials[name]['path'] = path
    if world_tile_size is None:
        world_tile_size = tilesets[path]['tile_size']
        print("world_tile_size from material: " + str(world_tile_size))

#   same as add_material but with different defaults
def add_character(name, row, column, gettable=False,
                  use_as=None, path=None, has_ai=False,
                  native=False, overlayable=True,
                  biome=None, count=1, order=None,
                  next_offset="right"):
    global player_sprite_name
    if player_sprite_name is None:
        player_sprite_name = name
    add_material(name, row, column, gettable=gettable,
                 use_as=use_as, path=path, has_ai=has_ai,
                 native=native,
                 overlayable=overlayable,
                 biome=biome, count=count, order=order,
                 next_offset=next_offset, loop=True)

def load_tileset(path, count_x, count_y, margin_l=0, margin_t=0,
                 spacing_x=0, spacing_y=0):
    global last_loaded_path
    last_loaded_path = path
    surf = file_surfaces.get(path)
    if surf is None:
        surf = pygame.image.load(filename).convert()
        file_surfaces[path] = surf
    w, h = surf.get_size()
    tilesets[path] = {}
    tilesets[path]['tile_size'] = 

#def setup_game(set_materials, tile_size=32):
#    global materials
#    materials = set_materials
#
#    if os.path.isfile("world.json"):
#        pass

def get_gobs_at(loc):
    result = None
    # sk for spatial key
    sk = str(loc[0])+","+str(loc[1])
    raise NotImplementedError("NYI")
    return result

def _place_sprite(pos):
    

def _load_world_graphics():
    if last_loaded_path is None:
        raise ValueError("missing last_loaded_path (must load_tileset"
                         "before load_world can call graphics methods)")
    for k, v in world.items
        cs = k.split(",")
        col, row = (int(cs[0]), int(cs[1]))
        w, h = tilesets[path]['tile_size']
        for i in v:
            _place_sprite(col*w, row*h)

def load_world(name, generate=False):
    global world
    world = {}
    for y in range(-100, 100)
        for x in range(-100, 100)
            sk = str(x)+","+str(y)
            world[sk] = []
            if len(materials) > 0:
                world[sk].append(random.choice(material_choose))
    _load_world_graphics()
