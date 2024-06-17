from dataclasses import dataclass
from typing import Optional
from web3 import Web3
import secrets
import struct

# Function to sign a message
def ecdsa_sign(sk, hash, curve):
    hash_int = int.from_bytes(hash, "big")
    k = secrets.randbelow(curve.n)
    p = curve.multiply_point(k, curve.G)
    if not curve.is_point_on_curve(p):
        return None
    r = p.x
    invk = pow(k, -1, curve.n)
    ad = (sk * r) % curve.n
    sum_m = (hash_int + ad) % curve.n
    s = (invk * sum_m) % curve.n

    return (r, s)

# Function to verify a signature
def ecdsa_verify(pk, hash, sign, curve):
    hash_int = int.from_bytes(hash, 'big')
    sinv = pow(sign[1], -1, curve.n)
    u1 = (hash_int * sinv) % curve.n
    u2 = (sign[0] * sinv) % curve.n
    p1 = curve.multiply_point(u1, curve.G)
    p2 = curve.multiply_point(u2, pk)
    res = curve.add_points(p1, p2)
    return sign[0] == res.x

# Class Point on the elliptic Curve
@dataclass
class Point:
    x: Optional[int] = None
    y: Optional[int] = None


# Class to implement elliptic curve operations
@dataclass
class EllipticCurveOperations:

    # Point addition
    def add_points(self, p1: Point, p2: Point) -> Point:

        if p1.x is None or p1.y is None:
            return p2

        if p2.x is None or p2.y is None:
            return p1

        if not self.is_point_on_curve(p1) or not self.is_point_on_curve(p2):
            raise ValueError(
                "Invalid input: One or both of the input points are not on the elliptic curve."
            )

        if p1 == p2:
            n = (3 * p1.x**2 + self.a) % self.p
            d = (2 * p1.y) % self.p
            try:
                inv = pow(d, -1, self.p)
            except ValueError:
                return Point()  # Point at infinity
            s = (n * inv) % self.p
            x_3 = (s**2 - p1.x - p1.x) % self.p
            y_3 = (s * (p1.x - x_3) - p1.y) % self.p
            return Point(x_3, y_3)
        else:
            n = (p2.y - p1.y) % self.p
            d = (p2.x - p1.x) % self.p
            try:
                inv = pow(d, -1, self.p)
            except ValueError:
                return Point()  # Point at infinity
            s = (n * inv) % self.p
            x_3 = (s**2 - p1.x - p2.x) % self.p
            y_3 = (s * (p1.x - x_3) - p1.y) % self.p
            return Point(x_3, y_3)

    # Function to negate a point
    def negate_point(self, p: Point) -> Point:
        if p.x is None or p.y is None:
            return Point()
        return Point(p.x, (-p.y) % self.p)

    # Function to perform the point subtraction
    def subtract_points(self, p1: Point, p2: Point) -> Point:
        neg_p2 = self.negate_point(p2)
        return self.add_points(p1, neg_p2)

    # Scalar Multiplication
    def multiply_point(self, k: int, p: Point) -> Point:

        if k == 0 or k >= self.n:
            raise ValueError("k is not in the range 0 < k < n")

        r = None

        num_bits = k.bit_length()

        for i in range(num_bits - 1, -1, -1):
            if r is None:
                r = p
                continue

            if r.x is None and r.y is None:
                r = p

            r = self.add_points(r, r)

            if (k >> i) & 1:
                if r.x is None and r.y is None:
                    r = p
                else:
                    r = self.add_points(r, p)
        return r

    # Check if a point belongs to the curve
    def is_point_on_curve(self, p: Point) -> bool:

        if p.x is None or p.y is None:
            return False
        # The equation of the curve is y^2 = x^3 + ax + b. We check if the point satisfies this equation.
        left_side = p.y**2 % self.p
        right_side = (p.x**3 + self.a * p.x + self.b) % self.p
        return left_side == right_side


# Class to create an elliptic curve
@dataclass
class EllipticCurve(EllipticCurveOperations):
    """
    p: is the order of the finite field Fp
    a: is the a constant of the elliptic curve
    b: is the b constant of the elliptic curve
    G: is the generator point of the abelian group G
    n: is the order of the abelian group Gn
    h: is the co-factor value
    """

    p: int
    a: int
    b: int
    G: Point
    n: int
    h: int
