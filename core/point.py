"""
Point has x,y,z coordinates and distance and transform methods.
"""
import numpy as np
from core.vector import Vector


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        """
        Add a Vector to this Point, returning a new Point.
        :param other: Vector or Point
        :return: Point
        """
        if isinstance(other, Vector):
            return Point(self.x + other.x, self.y + other.y, self.z + other.z)
        else:
            raise TypeError("Unsupported operand type: Point + {}".format(type(other)))

    def __sub__(self, other):
        """
        Subtract a Vector or Point from this Point, returning a Vector or Point.
        :param other: Vector or Point
        :return: Vector or Point
        """
        if isinstance(other, Point):
            return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
        elif isinstance(other, Vector):
            return Point(self.x - other.x, self.y - other.y, self.z - other.z)
        else:
            raise TypeError("Unsupported operand type: Point - {}".format(type(other)))

    def distance(self, other):
        """
        Calculate the distance between this Point and another Point.
        :param other: Point
        :return: float
        """
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)

    def transform(self, matrix):
        """
        Transform this Point using a 4x4 transformation matrix.
        :param matrix: 4x4 transformation matrix (list of lists)
        :return: Point
        """
        # Apply transformation matrix to the point
        x = self.x * matrix[0][0] + self.y * matrix[0][1] + self.z * matrix[0][2] + matrix[0][3]
        y = self.x * matrix[1][0] + self.y * matrix[1][1] + self.z * matrix[1][2] + matrix[1][3]
        z = self.x * matrix[2][0] + self.y * matrix[2][1] + self.z * matrix[2][2] + matrix[2][3]
        return Point(x, y, z)

    def __iter__(self):
        """
        Iterate over the coordinates of the Point.
        :return: iterator over (x, y, z)
        """
        return iter((self.x, self.y, self.z))
