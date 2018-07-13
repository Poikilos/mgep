# mgep
Minimal Game Engine for Pygame - More Assumptions, Less Typing

## Known Issues
* allow custom delay_count
* is iterator logic from pygame wiki's spritesheets wrong (the index
  is always 1 ahead of the frame)?
* move frame order logic from SpriteStripAnim to material

## Planned Features
~: low-priority
* Examples
* Flipping direction of graphics
* Transient effects (remove on animation end)
* Auto-generate credits
* Calculate hitboxes
* commands on specific frame of sprite
  * play sound
  * cause damage
  * move by vector
* stretch entire screen onto a `pg.Surface((w, h), pygame.SRCALPHA)`
* (~) color key
* (~) Recoloring
* (~) Sprite constructs with offsets (clothes, weapons, 2-square sprites)
* (~) Re-edging

## Changes

## Directives
mgep is intended for novices, elementary learners, and anyone who wants
to focus on the game creation process after writing few lines of code.
mgep allows you to create a game with the fewest lines possible by
making helpful assumptions.

## Usage
* place the mgep folder in the directory of your project
* `from mgep import *`
* for more information, see example*.py

## Helpful Assumptions
* loading a tileset makes a top view game
* adding sprites by row, col uses last loaded tileset
* walk speed based on real life: 2 meters per second, in 3 steps (such as left, right, left)
  --so delay_count is 20, so that sprite animations will always be 3 FPS (which is good for for sprite sheets with 3-frame [left, middle, right] animations, such as so-called "3x4" sprite sheets with `order=[1,2,1,3]`)
* if you do move_y by positive number, and have loaded a pose called 'walk.down', then the sprite's pose will be set to 'walk.down' 
* if you add a material more than once it will be more common
* if you run `stop_unit`, idle animation will be used, and if 'idle' key is not in `materials[sprite[what]]['tmp']['sprites']` dictionary, then `sprite['animate']` will be set to `False`.
  * keeps track of facing direction (if move_x and move_y are used) and look for 'idle.left' etc and only
    use 'idle' if no matching directional idle sprite key is found

## License
* License for media is CC0 unless otherwise specified in folders (you
must credit authors where there is an "Attribution" or "credits" file
that specifies and attribution license such as CC BY)
* License for everything else is GPL 3.0 unless changed at
https://github.com/poikilos/mgep/blob/master/LICENSE

## Developer Notes:
* col,row (y,x) order is ONLY used for referring to frames in a sprite sheet, and is always starting at 1,1 (which is at pixel position 0,0)
* loc or location (col,row format NOT row,col ) is always a cell location in the world database
* pos is a pixel location in the world (NOT on the screen generally)
* what SpriteSheet calls ticks is actually a frame count which multiplies each frame's duration
