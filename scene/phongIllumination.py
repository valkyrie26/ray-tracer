from scene.illuminationModel import IlluminationModel
from core.color import Color


class PhongIllumination(IlluminationModel):
    """
    Phong Illumination Model.
    """
    def __init__(self, ambient=0.2, diffuse=0.8, specular=0.1, specular_exponent=50):
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.specular_exponent = specular_exponent

    def illuminate(self, object_color, light_color, normal, light, view, material, intersection_point):
        """
            Phong illumination model
            :param object_color: Color of the object (Color object with rgb attribute)
            :param light_color: Color of the light source (Color object with rgb attribute)
            :param normal: Normal of the object (Vector)
            :param light: Light direction (Vector)
            :param view: View direction (Vector)
            :param material: Material of the object (dict with 'ambient_color', 'specular_color', etc.)
            :param intersection_point: Intersection point of the object (Point object)
            :return: Color of the object after illumination (Color object)
        """
        ambient_factor = self.ambient
        diffuse_factor = self.diffuse
        specular_factor = self.specular
        specular_exponent = self.specular_exponent

        # Extract RGB components
        object_r, object_g, object_b = object_color
        light_r, light_g, light_b = light_color
        ambient_r, ambient_g, ambient_b = material['ambient_color']
        specular_r, specular_g, specular_b = material['specular_color']

        # Ambient light
        ambient = (
            ambient_factor * ambient_r * object_r,
            ambient_factor * ambient_g * object_g,
            ambient_factor * ambient_b * object_b
        )

        # Diffuse light
        light_dir = light.normalize()
        diffuse_intensity = max(normal.dot(light_dir), 0)
        diffuse = (
            diffuse_intensity * diffuse_factor * object_r * light_r,
            diffuse_intensity * diffuse_factor * object_g * light_g,
            diffuse_intensity * diffuse_factor * object_b * light_b
        )

        # Specular light
        reflection = 2 * normal.dot(light_dir) * normal - light_dir
        specular_intensity = max(reflection.dot(view), 0) ** specular_exponent
        specular = (
            specular_intensity * specular_factor * specular_r * light_r,
            specular_intensity * specular_factor * specular_g * light_g,
            specular_intensity * specular_factor * specular_b * light_b
        )

        # Final color
        final_color = (
            ambient[0] + diffuse[0] + specular[0],
            ambient[1] + diffuse[1] + specular[1],
            ambient[2] + diffuse[2] + specular[2]
        )

        return Color(*final_color)
