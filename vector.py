import builtins
import math
from numbers import Number
import numpy as np


class Vec3:
    """Holds 3-elements tuple that represents a 3-dimensional vector"""
    def __init__(self, x=0.0, y=0.0, z=0.0):
        if isinstance(x, Vec3):
            (self.x, self.y, self.z) = (float(x.x), float(x.y), float(x.z))
        elif isinstance(x, tuple):
            (self.x, self.y, self.z) = (float(x[0]), float(x[1]), float(x[2]))
        elif isinstance(x, list):
            (self.x, self.y, self.z) = (float(x[0]), float(x[1]), float(x[2]))
        elif isinstance(x, np.ndarray):
            (self.x, self.y, self.z) = (float(x[0]), float(x[1]), float(x[2]))
        else:
            assert isinstance(x, Number)
            (self.x, self.y, self.z) = (float(x), float(y), float(z))

    def __str__(self):
        rounded = self.__round__(3)
        return f"<{rounded.x}, {rounded.y}, {rounded.z}>"

    def __repr__(self):
        rounded = self.__round__(3)
        return f"Vec3 Object: <{rounded.x}, {rounded.y}, {rounded.z}>"

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        assert not isinstance(scalar, Vec3)
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __truediv__(self, other):
        if isinstance(other, Vec3):
            return Vec3((self.x / other.x), (self.y / other.y), (self.z / other.z))
        else:
            assert isinstance(other, int) or isinstance(other, float)
            return Vec3((self.x / other), (self.y / other), (self.z / other))

    def dot(self, other):
        # assert isinstance(other, Vec3) # Caused issues with recursion?
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        assert isinstance(other, Vec3)
        if abs(self) != 0 and abs(other) != 0:
            i = self.y * other.z - self.z * other.y
            j = self.z * other.x - self.x * other.z
            k = self.x * other.y - self.y * other.x
            return Vec3(i, j, k)
        else:
            print(f"Issues with vectors {self} and {other}")
            print("Cannot take cross product of zero vector")

    def __abs__(self):
        return math.sqrt(self.dot(self))

    def __round__(self, num_dec=2):
        rounded_vec = Vec3(x=builtins.round(self.x, num_dec),
                           y=builtins.round(self.y, num_dec),
                           z=builtins.round(self.z, num_dec))
        return rounded_vec

    def normalize(self):
        magnitude = abs(self)
        if magnitude == 0.0:
            print("Warning: Attempted to normalize zero vector")
            return 0
        else:
            return self / magnitude


