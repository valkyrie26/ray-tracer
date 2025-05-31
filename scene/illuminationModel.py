"""
Class storing illumination models
"""


class IlluminationModel:
    """
    Abstract class for illumination models.
    """
    def illuminate(self, object_color, light_color, normal, light, view, material, intersection_point):
        raise NotImplementedError("Subclasses should implement this method.")
