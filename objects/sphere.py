"""
Sphere object for ray tracing.
"""

from objects.object import Object
import numpy as np
from core.point import Point
import math


class Sphere(Object):
    def __init__(self, center, radius, color, kr=0.0, kt=0.0, material=None, illumination_model='phong'):
        super().__init__(material, illumination_model)
        self.center = center  # Center of the sphere (Point)
        self.radius = radius
        self.color = color
        self.kr = kr  # Reflection coefficient
        self.kt = kt  # Transmission coefficient

    def intersect(self, ray):
        """
        Calculate intersection of a ray with the sphere.
        :param ray: Ray object with origin and direction.
        :return: A dictionary with intersection details if hit, otherwise None.
        """
        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        b = 2.0 * oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius ** 2
        discriminant = b ** 2 - 4 * a * c

        if discriminant < 0:
            return None  # No intersection

        t1 = (-b - np.sqrt(discriminant)) / (2.0 * a)
        t2 = (-b + np.sqrt(discriminant)) / (2.0 * a)

        t_values = [t for t in (t1, t2) if t > 0]
        if t_values:
            t = min(t_values)
            intersection_point = ray.origin + ray.direction * t
            normal = (intersection_point - self.center).normalize()

            # Spherical UV mapping with seam fix
            p = normal  # Already normalized direction from center
            theta = math.atan2(p.z, p.x)  # [-π, π]
            phi = math.acos(p.y)  # [0, π]

            # Wrap with epsilon to avoid u == 0 or u == 1 exactly (helps with seam)
            u = ((theta + math.pi) / (2 * math.pi)) % 1.0
            v = phi / math.pi

            # Small epsilon to nudge u away from hard edges
            epsilon = 1e-5
            if u < epsilon:
                u += epsilon
            elif u > 1.0 - epsilon:
                u -= epsilon

            return {
                't': t,
                'distance': t,
                'object': self,
                'normal': normal,
                'illumination_model': self.illumination_model,
                'material': self.material,
                'hit_point': intersection_point,
                'uv': (u, v)
            }

        return None

    def transform(self, matrix):
        """
        Apply a transformation matrix to the sphere.
        :param matrix: Transformation matrix (numpy array).
        :return: None
        """
        self.center = self.center.transform(matrix)
        self.invalidate_bounds()

    def get_bounds(self):
        """
        Get the axis-aligned bounding box of the sphere.
        :return: A tuple of two Points representing the minimum and maximum corners of the bounding box.
        """
        return Point(self.center.x - self.radius, self.center.y - self.radius, self.center.z - self.radius), \
            Point(self.center.x + self.radius, self.center.y + self.radius, self.center.z + self.radius)
