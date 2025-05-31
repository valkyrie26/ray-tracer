"""
Material class for representing the material properties of an object in a 3D scene.
"""


from core.color import Color


class Material:
    def __init__(self, ambient_color=Color(0, 0, 0), diffuse_color=(0, 0, 0), specular_color=Color(1, 1, 1),
                 specular_exponent=50):
        self.ambient_color = ambient_color
        self.diffuse_color = diffuse_color
        self.specular_color = specular_color
        self.specular_exponent = specular_exponent

    def __getitem__(self, item):
        return getattr(self, item)
