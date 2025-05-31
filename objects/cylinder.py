"""
Cylinder object for ray tracing.
"""

import numpy as np
import math
from core.ray import Ray
from core.point import Point
from core.vector import Vector
from objects.object import Object


class Cylinder(Object):
    """
    A finite cylinder aligned along the world‐Y axis, with flat caps.
    center: middle of the cylinder (Point)
    radius: cylinder radius
    height: total height along Y
    """
    def __init__(self, center, radius, height, color, kr=0.0, kt=0.0, material=None, illumination_model='phong'):
        super().__init__(material, illumination_model)
        self.center = center
        self.radius = radius
        self.height = height
        self.color = color
        self.kr, self.kt = kr, kt
        self.half_h = height / 2

        # Rotate cylinder from Y-axis to Z-axis (90° around X-axis)
        angle = math.radians(90)
        self.rotation_matrix = np.array([
            [1, 0, 0],
            [0, math.cos(angle), -math.sin(angle)],
            [0, math.sin(angle), math.cos(angle)],
        ])
        self.inv_rotation_matrix = np.linalg.inv(self.rotation_matrix)

    def intersect(self, ray: Ray):
        """
        Ray-cylinder intersection.
        :param ray: Ray object with origin and direction.
        :return: None if no intersection, otherwise a dictionary with t, object, normal, illumination_model, and material.
        """

        # Transform ray into cylinder's local coordinate system
        local_origin = ray.origin - self.center
        local_direction = ray.direction

        o = Point(*self.inv_rotation_matrix @ np.array([local_origin.x, local_origin.y, local_origin.z]))

        d = Vector(*self.inv_rotation_matrix @ np.array([local_direction.x, local_direction.y, local_direction.z]))

        # Intersect side surface (Y-axis aligned in local space)
        a = d.x ** 2 + d.z ** 2
        b = 2 * (o.x * d.x + o.z * d.z)
        c = o.x ** 2 + o.z ** 2 - self.radius ** 2

        t_cyl = None
        disc = b ** 2 - 4 * a * c
        if disc >= 0 and a != 0:
            sqrt_disc = math.sqrt(disc)
            for t in ((-b - sqrt_disc) / (2 * a), (-b + sqrt_disc) / (2 * a)):
                if t <= 1e-4:
                    continue
                y = o.y + d.y * t
                if -self.half_h <= y <= self.half_h:
                    if t_cyl is None or t < t_cyl:
                        t_cyl = t

        # Intersect flat caps
        t_cap = None
        if abs(d.y) > 1e-6:
            for cap_sign in (-1, 1):
                cap_y = cap_sign * self.half_h
                t = (cap_y - o.y) / d.y
                if t > 1e-4:
                    x = o.x + d.x * t
                    z = o.z + d.z * t
                    if x ** 2 + z ** 2 <= self.radius ** 2:
                        if t_cap is None or t < t_cap:
                            t_cap = t

        # Pick closest hit
        if t_cyl is not None and t_cap is not None:
            t_hit = min(t_cyl, t_cap)
        else:
            t_hit = t_cyl if t_cyl is not None else t_cap

        if t_hit is None:
            return None

        # Compute intersection point and local normal
        hit_local = o + d * t_hit

        if t_cap is not None and t_hit == t_cap:
            n_local = Vector(0, 1, 0 if hit_local.y > 0 else -1)
        else:
            n_local = Vector(hit_local.x, 0, hit_local.z).normalize()

        # Rotate back to world space
        P_world = self.center + Vector(*self.rotation_matrix @ np.array([hit_local.x, hit_local.y, hit_local.z]))
        n_world = Vector(*self.rotation_matrix @ np.array([n_local.x, n_local.y, n_local.z])).normalize()

        return {
            't': t_hit,
            'object': self,
            'normal': n_world,
            'illumination_model': self.illumination_model,
            'material': self.material,
        }

    def get_bounds(self):
        """
        Get the axis-aligned bounding box (AABB) of the cylinder.
        :return: A tuple of (min_point, max_point) representing the bounding box corners.
        """

        r = self.radius
        h = self.half_h

        # 8 corners in local (unrotated) space
        local_corners = [
            np.array([x, y, z], dtype=float)
            for x in [-r, r]
            for y in [-h, h]
            for z in [-r, r]
        ]

        # Center as a numpy array
        center_vec = np.array([self.center.x, self.center.y, self.center.z], dtype=float)

        # Transform corners to world space
        world_pts = [center_vec + self.rotation_matrix @ pt for pt in local_corners]
        world_pts = np.array(world_pts)

        min_p = Point(*world_pts.min(axis=0))
        max_p = Point(*world_pts.max(axis=0))
        return min_p, max_p


