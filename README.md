# mgep
Minimal Game Engine for Pygame - More Assumptions, Less Typing
![screenshot](https://raw.githubusercontent.com/poikilos/mgep/master/screenshot.jpg)
This demo is possible using 1 printable page of code in 10pt font

## Authors
* angles.py by phn on GitHub <https://gist.github.com/phn/1111712/35e8883de01916f64f7f97da9434622000ac0390>
* for media, see *CREDITS and Attribution text files in media folders
* all other work by poikilos (Jake Gustafson) unless noted alongside work such as in code comments

## Primary Features
* procedural:
  * less typing is required
  * any save method that takes dictionary can save game data
* responsive scaling for any narrow or wide screen ratio (maintain apparent pixel size)
* load sprites quickly and easily with specialized load_material, load_character, load_character_3x4,
  which all use tileset from last call to load_tileset
* framerate-independent sprite animation
* 3D metric positioning and physics

## Issues
~: low-priority
* allow custom delay_count
* is iterator logic from pygame wiki's spritesheets wrong (the index
  is always 1 ahead of the frame)?
* move frame order logic from SpriteStripAnim to material
* change from blit to blits for speed (Pygame 1.9.4 feature)
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
  * colorize specific parts: select set of colors, or select only >0% saturation area area or only 0% saturation area
* (~) Sprite constructs with offsets (clothes, weapons, 2-square sprites)
* (~) Re-edging
* (~) implement a callback binding system, to avoid issue: since offscreen buffer is used named `scalable_surf` and writing to it before or after calling draw_screen does nothing, and writing to screen after draw_screen doesn't scale what is drawn.
* (~) possibly switch to pypy-pygame for JavaScript support

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
* camera is similar to default opengl view space camera, where z is positive moving toward camera (but tilted upward, greater z also moves down toward bottom of screen)
* variable naming:
  * _mps: meters per second
  * _accel: meters per second squared
  * pose is a string referring to an animation, structured as `mode+'.'+cardinal` where cardinal is a direction ssuch as `'walk.N'`
  * heading is direction pointing, course is direction moving
  * agl is above ground level
  * horz is horizontal
  * vert is vertical
* optional unit values (to override defaults):
  * `'max_land_mps'`: maximum meters per second land speed
  * `'max_land_accel'`: maximum meters per second squared land speed
* col,row (y,x) order is ONLY used for referring to frames in a sprite sheet, and is always starting at 1,1 (which is at pixel position 0,0)
* loc or location (col,row format NOT row,col ) is always a cell location in the world database
* pos is a pixel location in the world (NOT on the screen generally)
* what SpriteSheet calls ticks is actually a frame count which multiplies each frame's duration
* removed junk from repo with following command:
  `git filter-branch --index-filter 'git rm --cached --ignore-unmatch sprites/blender-volumetric-particles-effects.zip'`
  * find name of object via (where b5c95b17a0eff5bf7025ab4c589df39c50ad95, a SHA1, is name of file in .git/objects):
    `git rev-list --objects --all | grep b5c95b17a0eff5bf7025ab4c589df39c50ad95`
  * file is still there for unknown reason (output of line above is "sprites/blender-volumetric-particles-effects.zip")
  * so instead used:
```
    #I'm not sure if the commented lines below are needed or not, because I ran them but they had errors:
    sudo wget https://raw.githubusercontent.com/nachoparker/git-forget-blob/master/git-forget-blob.sh -O /usr/local/bin/git-forget-blob
    sudo chmod +x /usr/local/bin/git-forget-blob
    git-forget-blob sprites/blender-volumetric-particles-effects.zip
    git remote add origin https://github.com/poikilos/mgep
    #git push -u origin master
    #git push -u origin --all
    #git push --set-upstream origin master
    git push -f origin master
```
  * other notes on purging:
    * to find the source of a large pack file, you must first get the blob hash from the idx file with the same name:
      `git verify-pack -v .git/objects/pack/pack-df5efcd46bf13fc31102a4eb682247f674562f07.idx | sort -k 3 -n | tail -10`
    * then get the filename from the blob hash same as further up (in this example, the corresponding pack file is "sounds/jute-dh-rpgsounds/fire_2.wav")
