# mgep
Minimal Game Engine for Pygame - More Assumptions, Less Typing
![screenshot](https://raw.githubusercontent.com/poikilos/mgep/master/screenshot.jpg)
This demo is possible using 1 printable page of code in 10pt font


## Installation
* pip install https://github.com/poikilos/mgep/zipball/master
  (or place the mgep/mgep folder in the directory of your project)

## Usage
* `from mgep import *`
* for more information, see example*.py
  * if you don't want the player to be able to use the F3 key, or any
    other engine hotkey: handle the key before `else` in keydown case.
    To eliminate use of all engine hotkeys, simply don't call
    `default_keydown`.

### Guiding Principles
mgep is intended for novices, elementary learners, and anyone who wants
to focus on the game creation process after writing few lines of code.
mgep allows you to create a game with the fewest lines possible by
making helpful assumptions.


### Helpful Assumptions
* loading a tileset makes a top view game
* adding sprites by col, row uses last loaded tileset
* walk speed based on real life: 2 meters per second, in 3 steps (such
  as left, right, left)
  --so delay_count is 20, so that sprite animations will always be 3 FPS
  (which is good for for sprite sheets with 3-frame
  [left, middle, right] animations, such as so-called "3x4"
  sprite sheets with `order=[1,2,1,3]`)
* if you do move_y by positive number, and have loaded a pose called
  'walk.down', then the sprite's pose will be set to 'walk.down'
* if you add a material more than once it will be more common
* if you run `stop_unit`, idle animation will be used, and if 'idle' key
  is not in `materials[sprite[what]]['tmp']['sprites']` dictionary, then
  `sprite['animate']` will be set to `False`.
  * keeps track of facing direction (if move_x and move_y are used) and
    look for 'idle.left' etc and only
    use 'idle' if no matching directional idle sprite key is found
* if you check what key is pressed you can call
  `default_keydown(event)` (potentially in an `else` clause) to get some
  useful debugging keys when using a keyboard (F3: visual debug; arrow
  keys: explore tilesets)
  * similar usage applies to calling:
    * (`if event.MOUSEBUTTONDOWN:`) `default_down`
    * (`if event.MOUSEBUTTONUP:`) `default_up`
    * (`if event.MOUSEMOTION:`) `default_motion`
* Generates normal map and mesa alpha from built-in terrain cutouts
* player has inventory
  * `set_unstackable` makes an item require a separate inventory slot
    * Only items that are unstackable are actually
      stored with all of their data in unit['items'] list of node dicts.
      Otherwise items are stored as a "material" in
      unit['materials'] dict where key is what, and value is a count
      (displayed in order of unit['material_slots'] string list).
  * `push_unit_item` adds an item to a unit's inventory
  * `pop_unit_what_item` gets certain type of item and removes it from
    unit's inventory
  * `pop_unit_item` gets item unit has selected, and removes it from
    unit's inventory
* `place_character` automatically loads file `name + ".json"` if
  present (present if you previously ran the program and have done
  `save(name, get_unit(name))` such as at end of program)

### Primary Features
* procedural:
  * less typing is required
  * any save method that takes dictionary can save game data
* responsive scaling for any narrow or wide screen ratio (maintain
  apparent pixel size)
* load sprites quickly and easily with specialized load_material,
  load_character, load_character_3x4, which all use tileset from last
  call to load_tileset
* framerate-independent sprite animation
* 3D metric positioning and physics
* percentage-based widget system that adapts to screen resolution
  changes instantly (pos and size are multiplied by screen size)
* Swipe events (simple angle only) are detected if swipe is as long as
  `settings['swipe_multiplier'] * short_px` where short_px is shorter
  dimension of screen detected.

### API Notes
* Settings should only be changed by editing "settings-mgep.json" after
  first run (including test run on developer's computer; or if you can
  write json yourself, make your own and mgep will automatically add any
  settings not present there)
* keeps track of mouse button data:
  * `button[1]` is dictionary with button data if left mouse button is
    pressed (also reserved for touch and serves as basis for touch
    guestures)
  * `button[x]['swiped']` is True if drag was already processed as a
    gesture.
* keeps track of mouse drag to interpret swipes, so mouse event (named
  `e` in the handlers) contains the following dictionary keys:
  * `e['state']` is a dict which is same as `button[x]` above.
  * See `def default_down` for other keys.
  * `on_tapped_node` occurs when time is shorter than
    `on_pushed_node` occurs otherwise.
* bind to events: `bind(name, function)` where function
  takes event dictionary (`e` in examples below) and name is:
  * 'draw_ui': `e['screen']` is the screen
  * 'swipe_angle': `e['angle']` is in degrees, `e['angle_rad']` in
    radians (also has mouse data)
  * 'swipe_direction': `e['direction']` is 'up', 'down', 'left', or
    'right' (also has 'swipe_angle' data above)
  * You can create an invisible jump button on the upper right quadrant
    of the screen:
```
def player_unit_jump(e):
    if not unit_jump(player_name, 5):
        show_popup("cannot jump while airborne")


add_widget((.5, 0), (.5, .5), f=player_unit_jump)

```

## Issues
~: low-priority enhancement\
!: high-priority\
+: enhancement
* <character name>.json, settings-mgep.json, and <world name>.json
  should be saved to user profile not directory if present, or app
  directory containing game in case not "..", instead of ".."
* (+) Use [Network Zero](https://networkzero.readthedocs.io/en/latest/)
  for ad-hoc networking
* (+) Provide instructions to package for Android using
  [RAPT](https://github.com/renpytom/rapt-pygame-example)
* (+) allow custom delay_count
* is iterator logic from pygame wiki's spritesheets wrong (the index
  is always 1 ahead of the frame)?
* move frame order logic from SpriteStripAnim to material
* (+) change from blit to blits for speed (Pygame 1.9.4 feature)
* (+) Examples
* (+) Allow flipping direction of graphics
* (+) Transient units such as explosions (remove unit on animation end)
* (+) Auto-generate credits
* (+!) Calculate hitboxes
* (+) commands on specific frame of sprite
  * play sound
  * cause damage
  * move by vector
* stretch entire screen onto a `pg.Surface((w, h), pygame.SRCALPHA)`
* (~) color key
* (~) colorize specific parts: select set of colors, or select only
  >0% saturation area area or only 0% saturation area
* (~) Sprite constructs with offsets (clothes, weapons, 2-square sprites)
* (~) Re-edging (soften hard edges)
* (~) implement a callback binding system, to avoid issue: since
  offscreen buffer is used named `scalable_surf` and writing to it
  before or after calling draw_screen does nothing, and writing to
  screen after draw_screen doesn't scale what is drawn.
* (~) possibly switch to pypy-pygame for JavaScript support
* (~) surfaces that affect physics: slippery, bouncy


## Authors
* angles.py by phn on GitHub
  <https://gist.github.com/phn/1111712/35e8883de01916f64f7f97da9434622000ac0390>
* for media, see *CREDITS and Attribution text files in media folders
* all other work by poikilos (Jake Gustafson) unless noted alongside
  work such as in code comments


## License
* License for media is CC0 unless otherwise specified in folders (you
must credit authors where there is an "Attribution" or "credits" file
that specifies and attribution license such as CC BY)
* License for everything else is GPL 3.0 unless changed at
https://github.com/poikilos/mgep/blob/master/LICENSE

## Developer Notes:
* run tests:
```bash
if [ -f "`command -v outputinspector`" ]; then
  nosetests 1>out.txt 2>err.txt
  outputinspector
else
  nosetests
fi
```
* additional tilesets to try/convert to 1/sqrt(2) ratio:
  * https://opengameart.org/content/zrpg-tiles
  * https://opengameart.org/content/castle-tiles-for-rpgs
    * split by author
  * https://opengameart.org/content/consolidated-hard-vacuum-terrain-tilesets
  * https://opengameart.org/content/2d-lost-garden-zelda-style-tiles-resized-to-32x32-with-additions
* camera is similar to default opengl view space camera, where z is
  positive moving toward camera (but tilted upward, greater z also moves
  down toward bottom of screen)
* material spec (dict with the following keys):
  * path: each material belongs to a tileset (saved as path string)
  * serials: dict of lists of tuples
    * serials[pose] is ALWAYS a list() even if pose is one frame
      * each tuple is an ordered pair of block in tileset for frame
    * subkey can be generated, but could also be special such as tr.grass
    * Coordinates are address as (x,y) by block (not pixel) starting at 1.
    * for top right of material such as mud where merges with grass,
    * or tr if material has alpha allowing merge with anything under it.
    * each item in the dict is a tile in the tileset.
  * overlayable: not yet implemented (true for characters, not for
    materials)
  * tmp: a dictionary which stores all runtime data that shouldn't be
    saved to human-readable json material file. This includes graphics,
    since graphics are referenced by the text as cell locations
      * material['tmp']['sprites'] is a dict of sprites
        * material['tmp']['sprites'][pose] is a sprite for a certain
          pose. A pose can include a variant, such as grass
  * mesa maps are chosen via bitwise math
    (see "mgep/etc/Mesa Connection, Automatic.jpg").
    The maps must be in 1/sqrt(2) ratio such as one of the (nearly)
    precise sizes shown by the dump_internal methods.
    The included maps (in maps/mesa) use 116x82 tiles.
* world spec:
  * world['gravity'] is a float in meters per second squared
  * world['blocks'] is a dict where key is a location such as '0,0'
    and each value is a list.
    * each list contains nodes
      * each node is a dict with 'what' and 'pose' strings
        where node['what'] is a material key and node['pose'] is a key
        for the material[node['what']]['tmp']['sprites'] dictionary.
  * world['tmp']['blocks'] holds locations of sprites for fast z-order:
    * world['tmp']['blocks'][key]['nodes'] is a list of nodes
      (see node format above)

* variable naming:
  * _mps: meters per second
  * _accel: meters per second squared
  * `pose` is a string referring to an animation, structured as
    `mode+'.'+cardinal` where cardinal is a direction--for example,
    `'walk.N'`.
  * `heading` is direction pointing, `course` is direction moving.
  * `agl` is above ground level
  * `horz` is horizontal
  * `vert` is vertical
* optional unit values (to override defaults):
  * `'max_land_mps'`: maximum meters per second land speed
  * `'max_land_accel'`: maximum meters per second squared land speed
* col,row (x, y, formerly row, col = y, x) order is used for referring
  to frames in a sprite sheet, and is always starting at 1,1 (which is
  at pixel position 0,0)
* loc or location (col, row format NOT row, col ) is always a cell
  location in the world database
* pos is a pixel location in the world (NOT on the screen generally)
* what SpriteSheet calls ticks is actually a frame count which
  multiplies each frame's duration
* removed junk from repo with following command:
  `git filter-branch --index-filter 'git rm --cached --ignore-unmatch sprites/blender-volumetric-particles-effects.zip'`
  * find name of object via (where b5c95b17a0eff5bf7025ab4c589df39c50ad95,
    a SHA1, is name of file in .git/objects):
    `git rev-list --objects --all | grep b5c95b17a0eff5bf7025ab4c589df39c50ad95`
  * file is still there for unknown reason (output of line above is
    "sprites/blender-volumetric-particles-effects.zip")
  * so instead used:
```
    # I'm not sure if the commented lines below are needed or not,
    # because I ran them but they had errors:
    sudo wget https://raw.githubusercontent.com/nachoparker/git-forget-blob/master/git-forget-blob.sh -O /usr/local/bin/git-forget-blob
    sudo chmod +x /usr/local/bin/git-forget-blob
    git-forget-blob sprites/blender-volumetric-particles-effects.zip
    git remote add origin https://github.com/poikilos/mgep
    # git push -u origin master
    # git push -u origin --all
    # git push --set-upstream origin master
    git push -f origin master
```
  * other notes on purging:
    * to find the source of a large pack file, you must first get the
      blob hash from the idx file with the same name:
      `git verify-pack -v .git/objects/pack/pack-df5efcd46bf13fc31102a4eb682247f674562f07.idx | sort -k 3 -n | tail -10`
    * then get the filename from the blob hash same as further up (in
      this example, the corresponding pack file is
      "sounds/jute-dh-rpgsounds/fire_2.wav")
* mesa maps
  * normal maps are generated (is standard normal map, so normal map RGB maps to XYZ, Z <= 0, and Z >= -1 where -1 faces light source for easy math [brightest when light vector and normal vector are coincident])
* Py4a vs Kivy's python-for-android vs pgs4a
  * Ways to run python on android:
    (https://en.wikibooks.org/wiki/Android/Kivy)
  * Py4a is successor to [pgs4a](https://launchpad.net/pgs4a)
  * pgs4a (http://pygame.renpy.org/) now points to
    <https://github.com/renpytom/rapt-pygame-example>
    (renpy is a visual novel engine, but github.com/renpy also holds:
    pygame_sdl2)
    * requires "JDK in the path, and Python 2.7 installed"
      (both 64-bit or both 32-bit)
    * import like:
```
try:
    import pygame_sdl2
    pygame_sdl2.import_as_pygame()
except ImportError:
    pass
```
  * "SL4A lets you run python scripts on android. Their PY4A is a step
    in their toolchain"
    - inclement
    "Kivy's python-for-android is more actively developed than
    SL4A(ASE)'s Py4A"
    - GozzoMan
    <https://stackoverflow.com/questions/18478492/difference-between-kivy-and-py4a>
  * Question about pgs4a on
    <http://forums.devshed.com/python-programming/976793-pgs4a-post2974402.html>
    is unanswered.
