"""
Color has rgb (floats), any floating point number
"""


class Color:
    def __init__(self, r, g, b):
        self.rgb = (r, g, b)  # RGB values as floats (0.0 to 1.0)

    def __mul__(self, scalar):
        """
        Multiply the Color by a scalar.
        :param scalar: A scalar value (int or float) to multiply the RGB values
        :return: A new Color object with RGB values multiplied by the scalar
        """
        if isinstance(scalar, (int, float)):
            return Color(self.rgb[0] * scalar, self.rgb[1] * scalar, self.rgb[2] * scalar)
        else:
            raise TypeError("Unsupported operand type: Color * {}".format(type(scalar)))

    def __add__(self, other):
        """
        Add another Color to this Color.
        :param other: Another Color object to add to this Color
        :return: A new Color object with RGB values added together
        """
        if isinstance(other, Color):
            return Color(self.rgb[0] + other.rgb[0], self.rgb[1] + other.rgb[1], self.rgb[2] + other.rgb[2])
        else:
            raise TypeError(f"Unsupported operand type: Color + {type(other)}")

    def __repr__(self):
        """
        String representation of the Color object.
        :return: String representation of the Color in RGB format.
        """
        return f"Color({self.rgb[0]}, {self.rgb[1]}, {self.rgb[2]})"

    def __iter__(self):
        """
        Iterate over the RGB values of the Color.
        :return: Iterator over the RGB values.
        """
        return iter(self.rgb)
