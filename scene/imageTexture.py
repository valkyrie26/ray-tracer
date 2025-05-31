from scene.illuminationModel import IlluminationModel
from core.color import Color
import numpy as np
from PIL import Image
import os


class ImageTexture(IlluminationModel):
    """
    Image-based texture sampling using per-object UV coordinates.
    Expects each object to supply UV in the intersection_point.x, intersection_point.y fields.
    """
    def __init__(self, image_path="image-textures/bumps.jpg"):
        # Load and normalize the image once
        img_full_path = os.path.join(image_path)
        img = Image.open(img_full_path).convert("RGB")
        # Store as float32 array in [0,1]
        self.tex = np.asarray(img, dtype=np.float32) / 255.0
        self.height, self.width, _ = self.tex.shape

    def illuminate(self,
                   object_color: Color,
                   light_color: Color,
                   normal,
                   light,
                   view,
                   material: dict,
                   intersection_point) -> Color:
        # Read UV directly from the intersection_point.x and .y
        u = intersection_point.x % 1.0
        v = intersection_point.y % 1.0

        # Convert to pixel indices
        px = int(u * (self.width - 1))
        py = int((1.0 - v) * (self.height - 1))  # flip v so 0 is bottom

        # Sample normalized array
        r, g, b = self.tex[py, px]
        return Color(r, g, b)
