"""
Class for procedural mosaic texture, child of illumination model class
"""

import random
import math
from core.color import Color
from scene.illuminationModel import IlluminationModel


class MosaicTexture(IlluminationModel):
    def __init__(self, cell_count=10, border_thickness=0.05, seed=42):
        self.cell_count = cell_count
        self.border_thickness = border_thickness
        self.seed = seed

    def illuminate(self, object_color, light_color,
                   normal, light, view, material, intersection_point):

        # 1) map to cell‐space
        u = intersection_point.x * self.cell_count
        v = intersection_point.y * self.cell_count
        cell_x = math.floor(u)
        cell_y = math.floor(v)

        min_d, second_d = float('inf'), float('inf')
        chosen_color = Color(0,0,0)

        # 2) site of nearest + 2nd-nearest in this cell + neighbors
        for ix in range(cell_x-1, cell_x+2):
            for iy in range(cell_y-1, cell_y+2):
                h = (ix*73856093 + iy*19349663 + self.seed) & 0xFFFFFFFF
                rng = random.Random(h)

                # pick its site globally
                sx = ix + rng.random()
                sy = iy + rng.random()

                # *** clamp random colors to [0.1, 0.8] for deeper tones ***
                color = Color(
                    rng.uniform(0.1, 0.8),
                    rng.uniform(0.1, 0.8),
                    rng.uniform(0.1, 0.8)
                )

                d = math.hypot(u - sx, v - sy)
                if d < min_d:
                    second_d, min_d = min_d, d
                    chosen_color = color
                elif d < second_d:
                    second_d = d

        # 3) border vs fill
        if (second_d - min_d) < self.border_thickness:
            return Color(0.05, 0.05, 0.05)

        # 4) simple contrast boost around mid-gray
        def boost(c):
            # c in [0,1] → remap so values <0.5 go darker, >0.5 go brighter
            contrast = 1.5
            return max(0.0, min(1.0, (c - 0.5)*contrast + 0.5))

        return Color(
            boost(chosen_color.rgb[0]),
            boost(chosen_color.rgb[1]),
            boost(chosen_color.rgb[2])
        )
