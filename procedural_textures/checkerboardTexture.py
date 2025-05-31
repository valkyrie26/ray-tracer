"""
Class for procedural checkerboard texture, child of illumination model class
"""

from scene.illuminationModel import IlluminationModel
from core.color import Color
import random


class CheckerboardTexture(IlluminationModel):
    def __init__(self, color1=Color(1, 0, 0), color2=Color(1, 1, 0), check_size=0.9, noise_probability=0.5):
        self.color1 = color1
        self.color2 = color2
        self.check_size = check_size
        self.noise_probability = noise_probability  # chance to introduce a noisy tile

    def illuminate(self, object_color, light_color, normal, light, view, material, intersection_point):
        """
        Illuminate the object using a checkerboard texture
        """
        # Calculate texture coordinates (u, v) from the intersection point
        u = intersection_point.x
        v = intersection_point.y

        # Scale the coordinates by the checkerboard size and take the fractional part
        u_scaled = (u * self.check_size) % 1
        v_scaled = (v * self.check_size) % 1

        # Determine the checkerboard pattern
        if (u_scaled < 0.5) ^ (v_scaled < 0.5):
            texture_color = self.color1
        else:
            texture_color = self.color2

        # Toggle for noise affecting the entire texture
        # if random.random() < self.noise_probability:
        #     noisy_rgb = tuple(
        #         min(max(c + random.uniform(-0.5, 0.5), 0), 1)
        #         for c in texture_color.rgb
        #     )
        #     return Color(*noisy_rgb)

        # Toggle for noise affecting individual tiles
        
        # # Identify which tile we are in
        # tile_x = int(u * self.check_size)
        # tile_y = int(v * self.check_size)
        # tile_id = hash((tile_x, tile_y)) % 1000  # keep value small
        # if tile_id / 1000.0 < self.noise_probability:
        #     noisy_rgb = tuple(
        #         min(max(c + random.uniform(-0.5, 0.5), 0), 1)
        #         for c in texture_color.rgb
        #     )
        #     return Color(*noisy_rgb)

        return texture_color
