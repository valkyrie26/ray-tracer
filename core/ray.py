"""
Ray has an origin and direction
"""


class Ray:
    def __init__(self, origin, direction, space=None):
        self.origin = origin  # Origin of the ray (Point)
        self.direction = direction.normalize()  # Direction of the ray (Vector)
        self.space = space  # The object that spawned this ray


