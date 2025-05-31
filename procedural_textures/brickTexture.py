"""
Class for procedural brick texture, child of illumination model class
"""

from scene.illuminationModel import IlluminationModel
from core.color import Color
import math


class BrickTexture(IlluminationModel):
    def __init__(
        self,
        brick_color1=Color(0.6, 0.1, 0.1),  # reddish brick
        brick_color2=Color(0.5, 0.05, 0.05),  # darker variant
        mortar_color=Color(0.85, 0.85, 0.85),  # light gray
        brick_width=1.0,
        brick_height=0.5,
        mortar_thickness=0.05,
    ):
        self.brick_color1 = brick_color1
        self.brick_color2 = brick_color2
        self.mortar_color = mortar_color
        self.brick_width = brick_width
        self.brick_height = brick_height
        self.mortar_thickness = mortar_thickness

    def illuminate(self, object_color, light_color, normal, light, view, material, intersection_point):
        u = intersection_point.x
        v = intersection_point.y

        # Compute which row and column this point is in
        row = math.floor(v / self.brick_height)
        col = math.floor((u + (self.brick_width / 2 if row % 2 else 0)) / self.brick_width)

        # Compute local position within the brick tile
        u_mod = (u + (self.brick_width / 2 if row % 2 else 0)) % self.brick_width
        v_mod = v % self.brick_height

        # Mortar check
        if u_mod < self.mortar_thickness or v_mod < self.mortar_thickness:
            return self.mortar_color

        # Choose alternating brick colors
        if (row + col) % 2 == 0:
            return self.brick_color1
        else:
            return self.brick_color2
