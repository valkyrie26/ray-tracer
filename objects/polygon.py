"""
Polygon is a type of Object with 3 vertices and a normal vector. It is also used to create a cuboid.
"""

from objects.object import Object
from core.point import Point


class Polygon(Object):
    def __init__(self, vertices, color=None, normal=None, uvs=None, kr=0.0, kt=0.0, material=None,
                 illumination_model='phong'):
        super().__init__(material, illumination_model)
        self.vertices = vertices
        self.normal = normal if normal is not None else self.calculate_normal()
        self.uvs = uvs if uvs else [(0, 0), (0, 0), (0, 0)]  # default fallback

        self.color = color
        self.kr = kr
        self.kt = kt

    def calculate_normal(self):
        """
        Calculate the normal vector of the polygon defined by its vertices.
        :return: Normalized normal vector.
        """
        v0, v1, v2 = self.vertices
        edge1 = v1 - v0
        edge2 = v2 - v0
        normal = edge1.cross(edge2).normalize()
        return normal

    def intersect(self, ray):
        """
        Ray-polygon intersection using Möller–Trumbore algorithm.
        :param ray: Ray object with origin and direction.
        :return: None if no intersection, otherwise a dictionary with intersection details.
        """
        v0, v1, v2 = self.vertices
        e1 = v1 - v0
        e2 = v2 - v0
        h = ray.direction.cross(e2)
        a = e1.dot(h)

        epsilon = 1e-6
        if abs(a) < epsilon:
            return None

        f = 1 / a
        s = ray.origin - v0
        beta = f * s.dot(h)
        if beta < 0 or beta > 1:
            return None

        q = s.cross(e1)
        gamma = f * ray.direction.dot(q)
        if gamma < 0 or beta + gamma > 1:
            return None

        t = f * e2.dot(q)
        if t > epsilon:
            # For image texture mapping, we need to calculate the UV coordinates
            (u0, v0), (u1, v1), (u2, v2) = self.uvs
            u = (1 - beta - gamma) * u0 + beta * u1 + gamma * u2
            v = (1 - beta - gamma) * v0 + beta * v1 + gamma * v2

            return {
                't': t,
                'distance': t,
                'object': self,
                'normal': self.normal,
                'illumination_model': self.illumination_model,
                'material': self.material,
                'hit_point': ray.origin + ray.direction * t,
                'uv': (u, v)
            }
        return None

    def transform(self, matrix):
        """
        Transform the polygon by applying a transformation matrix to its vertices and normal vector.
        :param matrix: Transformation matrix to apply.
        :return: None
        """
        self.vertices = [v.transform(matrix) for v in self.vertices]
        # Transform the normal vector using the inverse transpose of the matrix
        self.normal = self.normal.transform(matrix.inverse().transpose()).normalize()
        self.invalidate_bounds()  # Critical for KD-tree updates

    def get_bounds(self):
        """
        Calculate the axis-aligned bounding box (AABB) for the polygon.
        :return: Tuple of two Points representing the minimum and maximum bounds.
        """
        if not self.vertices:
            return None

        # Initialize min and max with first vertex
        min_x = max_x = self.vertices[0].x
        min_y = max_y = self.vertices[0].y
        min_z = max_z = self.vertices[0].z

        # Find the min/max bounds by checking all vertices
        for vertex in self.vertices[1:]:
            min_x = min(min_x, vertex.x)
            max_x = max(max_x, vertex.x)
            min_y = min(min_y, vertex.y)
            max_y = max(max_y, vertex.y)
            min_z = min(min_z, vertex.z)
            max_z = max(max_z, vertex.z)

        return Point(min_x, min_y, min_z), Point(max_x, max_y, max_z)

