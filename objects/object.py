"""
Object in our 3D space, it has material and illumination_model. Abstract class
"""

from scene.phongIllumination import PhongIllumination
from scene.blinnPhongIllumination import BlinnPhongIllumination
from procedural_textures.checkerboardTexture import CheckerboardTexture
from procedural_textures.brickTexture import BrickTexture
from procedural_textures.mandelbrotTexture import MandelbrotTexture
from procedural_textures.mosaicTexture import MosaicTexture
from scene.imageTexture import ImageTexture
from core.color import Color
import uuid

# Note: Any new illumination model should be added here
illumination_models = {
            'phong': PhongIllumination,
            'blinn-phong': BlinnPhongIllumination,
            'checkerboard': CheckerboardTexture,
            'brick': BrickTexture,
            'mandelbrot': MandelbrotTexture,
            'image': ImageTexture,
            'mosaic': MosaicTexture,
        }


class Object:
    def __init__(self, material=None, illumination_model='phong'):
        self.material = material or {
            'ambient_color': Color(0.1, 0.1, 0.1),
            'specular_color': Color(1, 1, 1),
            'shininess': 50
        }

        if illumination_model in illumination_models:
            self.illumination_model = illumination_models[illumination_model]()
        else:
            print("[Warning] Unknown illumination model '{illumination_model}', defaulting to 'phong'")
            self.illumination_model = PhongIllumination()

        self._cached_bounds = None
        self.object_id = uuid.uuid4()

    def get_bounds(self):
        """
        Get the bounds of the object. This should be implemented by subclasses.
        :return: A tuple representing the bounds of the object (min_x, min_y, min_z, max_x, max_y, max_z).
        """
        if self._cached_bounds is None:
            self._cached_bounds = self.get_bounds()  # Subclass should implement this method
        return self._cached_bounds

    def invalidate_bounds(self):
        """
        Invalidate the cached bounds of the object. This should be called whenever the object changes
        :return: None
        """
        self._cached_bounds = None

    def intersect(self, ray):
        """
        Check if the ray intersects with the object.
        :param ray: The ray to check for intersection.
        :return: A tuple containing the intersection point and normal vector if there is an intersection,
        """
        raise NotImplementedError("Subclasses must implement intersect method")

    def transform(self, matrix):
        """
        Apply a transformation matrix to the object.
        :param matrix: The transformation matrix to apply.
        :return: None
        """
        # Apply transformation matrix to the object
        pass  # Implement transformation logic

