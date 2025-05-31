"""
Torus object implementation for ray tracing.
"""

import numpy as np, math
from objects.object import Object
from core.point import Point
from core.vector import Vector


class Torus(Object):
    def __init__(self,
                 center: Point,
                 major_radius: float,
                 minor_radius: float,
                 color,
                 kr=0.0,
                 kt=0.0,
                 material=None,
                 illumination_model='phong'):
        super().__init__(material, illumination_model)
        self.center = center
        self.R = major_radius
        self.r = minor_radius
        self.color = color
        self.kr = kr
        self.kt = kt

    def intersect(self, ray):
        """
        Intersect a ray with the torus object.
        :param ray: Ray object with origin and direction.
        :return: A dictionary with intersection details if hit, otherwise None.
        """
        # move into torus‐local space
        O = ray.origin - self.center
        D = ray.direction

        # helper dot products
        Ox, Oy, Oz = O.x, O.y, O.z
        Dx, Dy, Dz = D.x, D.y, D.z
        R, r = self.R, self.r

        # build quartic coefficients for: (||P(t)||^2 + R^2 - r^2)^2 - 4R^2 (Px^2 + Pz^2) = 0
        G = D.dot(D)
        H = 2 * O.dot(D)
        I = O.dot(O) + R*R - r*r

        coeff4 = G*G
        coeff3 = 2*G*H
        coeff2 = 2*G*I + H*H - 4*R*R*(Dx*Dx + Dz*Dz)
        coeff1 = 2*H*I - 8*R*R*(Dx*Ox + Dz*Oz)
        coeff0 = I*I - 4*R*R*(Ox*Ox + Oz*Oz)

        # solve quartic
        roots = np.roots([coeff4, coeff3, coeff2, coeff1, coeff0])
        # pick the smallest positive real root
        ts = [rt.real for rt in roots if abs(rt.imag) < 1e-6 and rt.real > 1e-5]
        if not ts:
            return None
        t = min(ts)
        P = ray.origin + ray.direction * t

        # compute normal via gradient of implicit function
        # at local P': (x,y,z) = (P - center)
        loc = P - self.center
        x, y, z = loc.x, loc.y, loc.z
        sum2 = x*x + y*y + z*z + R*R - r*r
        nx = 4*x*sum2 - 8*R*R*x
        ny = 4*y*sum2
        nz = 4*z*sum2 - 8*R*R*z
        normal = Vector(nx, ny, nz).normalize()

        # UV mapping
        # u: around the big circle
        theta = math.atan2(z, x)
        u = ((theta + math.pi) / (2*math.pi)) % 1.0

        # find the center of the tube circle at that theta
        cx = R * math.cos(theta)
        cz = R * math.sin(theta)
        # v: around the small circle (φ)
        vx = x - cx
        vz = z - cz
        phi = math.atan2(y, math.hypot(vx, vz))
        v = (phi / (2*math.pi)) + 0.5

        # nudge off seams
        eps = 1e-5
        u = min(max(u, eps), 1-eps)
        v = min(max(v, eps), 1-eps)

        return {
            't': t,
            'distance': t,
            'object': self,
            'normal': normal,
            'illumination_model': self.illumination_model,
            'material': self.material,
            'hit_point': P,
            'uv': (u, v)
        }

    def transform(self, matrix):
        """
        Transform the torus by applying a transformation matrix.
        :param matrix: Transformation matrix to apply.
        :return: None
        """
        # just move the center
        self.center = self.center.transform(matrix)
        self.invalidate_bounds()

    def get_bounds(self):
        """
        Get the axis-aligned bounding box of the torus.
        :return: A tuple of two Points representing the minimum and maximum corners of the bounding box.
        """
        # axis-aligned box: major+minor in x/z, minor in y
        R, r = self.R, self.r
        cx, cy, cz = self.center.x, self.center.y, self.center.z
        min_pt = Point(cx - (R + r), cy - r, cz - (R + r))
        max_pt = Point(cx + (R + r), cy + r, cz + (R + r))
        return min_pt, max_pt
