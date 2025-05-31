"""
Vector class has x,y,z attributes, +, -, cross, dot, length, normalize, and transform methods.
"""

import numpy as np


class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        """
        Add two vectors together.
        :param other: Another Vector instance to add.
        :return: A new Vector instance representing the sum of the two vectors.
        """
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        """
        Subtract another vector from this vector.
        :param other: Another Vector instance to subtract.
        :return: A new Vector instance representing the difference of the two vectors.
        """
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self):
        """
        Negate the vector.
        :return: A new Vector instance representing the negation of this vector.
        """
        return Vector(-self.x, -self.y, -self.z)

    def __mul__(self, scalar):
        """
        Multiply the vector by a scalar.
        :param scalar: An integer or float to multiply the vector by.
        :return: A new Vector instance representing the product of the vector and the scalar.
        """
        if isinstance(scalar, (int, float)):
            return Vector(self.x * scalar, self.y * scalar, self.z * scalar)
        raise TypeError("Multiplication is only supported with int or float.")

    def __truediv__(self, other):
        """
        Divide the vector by a scalar.
        :param other: An integer or float to divide the vector by.
        :return: A new Vector instance representing the quotient of the vector and the scalar.
        """
        return Vector(self.x / other, self.y / other, self.z / other)

    def __rmul__(self, scalar):
        """
        Right multiplication of the vector by a scalar.
        :param scalar: An integer or float to multiply the vector by.
        :return: A new Vector instance representing the product of the scalar and the vector.
        """
        return self.__mul__(scalar)

    def cross(self, other):
        """
        Calculate the cross product of this vector with another vector.
        :param other: Another Vector instance to cross with.
        :return: A new Vector instance representing the cross product of the two vectors.
        """
        return Vector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def dot(self, other):
        """
        Calculate the dot product of this vector with another vector.
        :param other: Another Vector instance to dot with.
        :return: A float representing the dot product of the two vectors.
        """
        return self.x * other.x + self.y * other.y + self.z * other.z

    def length(self):
        """
        Calculate the length (magnitude) of the vector.
        :return: A float representing the length of the vector.
        """
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        """
        Normalize the vector to unit length.
        :return: A new Vector instance representing the normalized vector.
        """
        length = self.length()
        if length == 0:
            return Vector(0, 0, 0)  # Default to zero vector if length is zero
        return Vector(self.x / length, self.y / length, self.z / length)

    def transform(self, matrix):
        """
        Transform the vector using a transformation matrix.
        :param matrix: A 4x4 transformation matrix (as a list of lists or numpy array).
        :return: A new Vector instance representing the transformed vector.
        """
        # Apply transformation matrix to the vector
        pass  # Implement matrix transformation logic

    def to_tuple(self):
        """
        Convert the vector to a tuple.
        :return: A tuple (x, y, z) representing the vector.
        """
        return self.x, self.y, self.z
