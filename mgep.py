try:
    import pygame
except:
    print("You must install pygame:")
    print("dnf install -y python3-pygame")
    exit(1)

# the world is a 

tilesets = {}
materials = {}
world = {}

last_loaded_path = None
# material spec:
# path: each material belongs to a tileset (saved as path string)
# frame_locs: dict of tuples (coordinates of block in tileset).
#   subkey can be generated, but could also be special such as tr.grass
#   Coordinates are address as (x,y) by block (not pixel) starting at 1.
#   for top right of material such as mud where merges with grass,
#   or tr if material has alpha allowing merge with anything under it.
#   each item in the dict is a tile in the tileset.
#   Also, subkey can be animated: 1[1] where [1] is frame starting at 1.

def _add_sprite_type(name, cells, gettable=True,
                     subkey=None, path=None, has_ai=False,
                     native=True, overlayable=False,
                     biome="default"):
    if path is None:
        path = last_loaded_path
    material = None
    material = materials.get(name, None)  # default to new material
    if material is None:
        material = {}
        materials[name] = material
    if subkey is None:
        try_sub_i = 0
        try_sub = str(try_sub_i)
        mfr=material.get("frame_locs")
        if mfr is not None:
            while try_sub in mfr:
                try_sub_i += 1
                try_sub = str(try_sub_i)
        else:
            material["frame_locs"] = {}
        subkey = try_sub
    material["frame_locs"][subkey] = cells
    material["overlayable"] = overlayable
    material["biome"] = biome

# gettable allows player to get material
# path: if None, then uses last loaded tileset
def add_material(name, row, column, gettable=True,
                 subkey=None, path=None, has_ai=False,
                 native=True, overlayable=False,
                 biome="default"):
    cells = [(row, column)]
    _add_sprite_type(name, cells, gettable=gettable,
                 subkey=subkey, path=path, has_ai=has_ai,
                 native=native,
                 overlayable=overlayable,
                 biome=biome)

#   same as add_material but with different defaults
def add_character(name, row, column, gettable=False,
                  subkey=None, path=None, has_ai=False,
                  native=False, overlayable=True,
                  biome=None):
    add_material(name, row, column, gettable=gettable,
                 subkey=subkey, path=path, has_ai=has_ai,
                 native=native,
                 overlayable=overlayable,
                 biome=biome)


def load_tileset(path, across, down, margin_l=0, margin_t=0,
                 spacing_x=0, spacing_y=0):
    global last_loaded_path
    last_loaded_path = path

def setup_game(set_materials, block_size=32):
    global materials
    materials = set_materials

if os.path.isfile("world.json"):
    pass

def get_gob_at(pos):
    # ss for spatial string
    ss = str(pos[0])+","+"str(pos[1])
