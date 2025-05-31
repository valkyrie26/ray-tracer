"""
A class representing a 3D cuboid object with methods for intersection, transformation, and bounding box calculation.
"""
from objects.object import Object
from objects.polygon import Polygon
from core.vector import Vector
from core.point import Point


class Cuboid(Object):
    def __init__(self, center, width, height, depth, color, kr=0.0, kt=0.0, material=None, illumination_model='phong'):
        super().__init__(material, illumination_model)

        self.center = center
        self.width = width
        self.height = height
        self.depth = depth
        self.color = color
        self.kr = kr
        self.kt = kt
        self.triangles = self.create_cuboid()

    def create_cuboid(self):
        """
        Create the triangles that make up the cuboid.
        :return: List of Polygon objects representing the cuboid's triangles.
        """
        cx, cy, cz = self.center
        w, h, d = self.width, self.height, self.depth

        # 8 corner points
        v = [
            Point(cx - w / 2, cy - h / 2, cz - d / 2),  # 0
            Point(cx + w / 2, cy - h / 2, cz - d / 2),  # 1
            Point(cx + w / 2, cy + h / 2, cz - d / 2),  # 2
            Point(cx - w / 2, cy + h / 2, cz - d / 2),  # 3
            Point(cx - w / 2, cy - h / 2, cz + d / 2),  # 4
            Point(cx + w / 2, cy - h / 2, cz + d / 2),  # 5
            Point(cx + w / 2, cy + h / 2, cz + d / 2),  # 6
            Point(cx - w / 2, cy + h / 2, cz + d / 2),  # 7
        ]

        # Precompute UVs for each vertex per projection axis
        uv_xy = [((pt.x / w + 0.5), (pt.y / h + 0.5)) for pt in v]
        uv_yz = [((pt.y / h + 0.5), (pt.z / d + 0.5)) for pt in v]
        uv_xz = [((pt.x / w + 0.5), (pt.z / d + 0.5)) for pt in v]

        # Face definitions: (indices, normal, uv_set)
        faces = [
            ([0, 1, 2, 3], Vector(0, 0, -1), uv_xy),  # Front
            ([5, 4, 7, 6], Vector(0, 0, 1), uv_xy),  # Back
            ([4, 0, 3, 7], Vector(-1, 0, 0), uv_yz),  # Left
            ([1, 5, 6, 2], Vector(1, 0, 0), uv_yz),  # Right
            ([3, 2, 6, 7], Vector(0, 1, 0), uv_xz),  # Top
            ([4, 5, 1, 0], Vector(0, -1, 0), uv_xz),  # Bottom
        ]

        triangles = []
        for (i0, i1, i2, i3), normal, uvs in faces:
            tri1 = Polygon(
                vertices=[v[i0], v[i1], v[i2]],
                normal=normal,
                uvs=[uvs[i0], uvs[i1], uvs[i2]]
            )
            tri2 = Polygon(
                vertices=[v[i0], v[i2], v[i3]],
                normal=normal,
                uvs=[uvs[i0], uvs[i2], uvs[i3]]
            )
            triangles.extend([tri1, tri2])

        return triangles

    def intersect(self, ray):
        """
        Check if the ray intersects with the cuboid.
        :param ray: Ray object representing the ray to check for intersection.
        :return: A dictionary with intersection details if the ray intersects, otherwise None.
        """
        closest_hit = None
        for triangle in self.triangles:
            hit = triangle.intersect(ray)
            if hit and (closest_hit is None or hit['t'] < closest_hit['t']):
                # Copy the polygon’s hit but *override* all the fields
                closest_hit = {
                    't': hit['t'],
                    'distance': hit.get('distance', hit['t']),
                    'object': self,
                    'hit_point': hit['hit_point'],
                    'uv': hit['uv'],
                    'normal': hit['normal'],
                    'material': self.material,
                    'illumination_model': self.illumination_model
                }

        return closest_hit

    def transform(self, matrix):
        """
        Transform the cuboid by applying a transformation matrix.
        :param matrix: Transformation matrix to apply to the cuboid.
        :return: None
        """
        self.center = self.center.transform(matrix)
        for triangle in self.triangles:
            triangle.transform(matrix)
        self.invalidate_bounds()  # Critical for KD-tree updates

    def get_bounds(self):
        """
        Calculate the axis-aligned bounding box of the cuboid.
        :return: A tuple of two Points representing the minimum and maximum corners of the bounding box.
        """
        min_x = self.center.x - self.width / 2
        max_x = self.center.x + self.width / 2
        min_y = self.center.y - self.height / 2
        max_y = self.center.y + self.height / 2
        min_z = self.center.z - self.depth / 2
        max_z = self.center.z + self.depth / 2

        return Point(min_x, min_y, min_z), Point(max_x, max_y, max_z)

