"""
Class for procedural mandelbrot texture, child of illumination model class
"""

from scene.illuminationModel import IlluminationModel
from core.color import Color
import math


class MandelbrotTexture(IlluminationModel):
    def __init__(
        self,
        zoom=7,
        center_x=-0.75,
        center_y=0.0,
        max_iter=300
    ):
        self.zoom = zoom
        self.center_x = center_x
        self.center_y = center_y
        self.max_iter = max_iter
        self.inside_color = Color(0.0, 0.0, 0.0)

    def mandelbrot_smooth(self, c):
        z = 0
        for n in range(self.max_iter):
            z = z * z + c
            if abs(z) > 2:
                # Smooth iteration count
                return n + 1 - math.log(math.log(abs(z))) / math.log(2)
        return self.max_iter

    def map_color(self, t):
        # Map t ∈ [0, 1] to blue → white gradient
        r = min(1.0, t * 4.0)  # ramps up fast
        g = min(1.0, t * t * 1.5)
        b = min(1.0, 0.5 + t)
        return Color(r, g, b)

    def illuminate(self, object_color, light_color, normal, light, view, material, intersection_point):
        u = intersection_point.x
        v = intersection_point.y

        # Normalize to viewport [-1, 1]
        u_norm = u * 2.0
        v_norm = v * 2.0

        # Map to complex plane
        x = (u_norm - self.center_x) / self.zoom
        y = (v_norm - self.center_y) / self.zoom
        c = complex(x, y)

        smooth_iter = self.mandelbrot_smooth(c)

        if smooth_iter >= self.max_iter:
            return self.inside_color
        else:
            t = smooth_iter / self.max_iter
            return self.map_color(t)

