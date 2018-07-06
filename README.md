# mgep
Minimal Game Engine for Pygame - More Assumptions, Less Typing

## Planned Features
~: low-priority
* Examples
* Flipping direction of graphics
* Transient effects (remove on animation end)
* Auto-generate credits
* Calculate hitboxes
* frame commands
  * play sound
  * cause damage
  * move by vector
* (~) color key
* (~) Recoloring
* (~) Sprite overlays (clothes, weapons, 2-square sprites)
* (~) Re-edging

## Directives
mgep is intended for novices, elementary learners, and anyone who wants
to focus on the game creation process after writing few lines of code.
mgep allows you to create a game with the fewest lines possible by
making helpful assumptions.

## Usage

## Helpful Assumptions
* loading a tileset makes a top view game
* adding sprites by row, col uses last loaded tileset
* first sprite added via add_sprite is the player
* walk speed based on real life: 2 meters per second, in 3 steps (such as left, right, left)

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
