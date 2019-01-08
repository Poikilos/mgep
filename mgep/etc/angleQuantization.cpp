// 8-directional quantization below is from
// <https://www.gamedev.net/forums/topic/679371-3d-8-directional-
// sprite-rotation-based-on-facing-direction-relative-to-
// camera-direction/>
// Camera facing direction (in 2D)
// Direction is the direction at which the camera is looking at
// ( in 2D )
vec2 camera = vec2(
           cos(degtorad(CCamera::GetMainCamera()->transform.direction)),
           -sin(degtorad (CCamera::GetMainCamera()->transform.direction)));  // Object facing direction (in 2D)
              // direction is the facing direction of the sprite, i.e. the direction at which the sprite is Looking At. ( in 2D )
vec2 facing = vec2(
           cos(degtorad(self->transform->direction)),
           -sin(degtorad(self->transform->direction)));  // Dot product
double cosine = dot(camera, facing);
double angle = radtodeg(arctan2(facing.y, facing.x) - arctan2(camera.y, camera.x));
if (angle > 90.0) {
    angle = 450.0 - angle; }
else {
   angle = 90.0 - angle;}
self->sprite = sprite_set[floor(angle / 45.0)];
