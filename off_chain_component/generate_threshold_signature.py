import sys
sys.path.insert(1, '../threshold-ecdsa-in-off-chain-components/off_chain_component')
import random
import secrets
from hashlib import sha256
from dataclasses import dataclass
from typing import Optional, List, Tuple
from elliptic_curve_operations import Point, EllipticCurve
from shamir_secret_sharing import generate_polynomial, evaluate_polynomial, share_secret, reconstruct_secret

# Function to generate partial signatures
def generate_partial_signatures(shares, message, curve):
    partial_signatures = []
    k = secrets.randbelow(curve.numnodes)
    R = curve.multiply_point(k, curve.G)
    r = R.x % curve.numnodes
    k_inv = pow(k, -1, curve.numnodes)
    z = message % curve.numnodes
    for x, y in shares:
        s = (k_inv * (z + r * y)) % curve.numnodes
        partial_signatures.append((x, s))
    return R, partial_signatures

# Function to combine partial signatures
def combine_partial_signatures(R, partial_signatures, curve):
    s = 0
    for x, partial_s in partial_signatures:
        numerator = 1
        denominator = 1
        for x_j, _ in partial_signatures:
            if x != x_j:
                numerator = (numerator * (-x_j)) % curve.numnodes
                denominator = (denominator * (x - x_j)) % curve.numnodes
        lagrange_coefficient = numerator * pow(denominator, -1, curve.numnodes) % curve.numnodes
        s = (s + partial_s * lagrange_coefficient) % curve.numnodes
    return (R.x % curve.numnodes, s)

# Function to verify the final signature
def verify_signature(pk, message, signature, curve):
    r, s = signature
    if not (1 <= r <= curve.numnodes - 1) or not (1 <= s <= curve.numnodes - 1):
        return False
    z = int.from_bytes(sha256(message.encode()).digest(), 'big') % curve.numnodes
    s_inv = pow(s, -1, curve.numnodes)
    u1 = (z * s_inv) % curve.numnodes
    u2 = (r * s_inv) % curve.numnodes
    p1 = curve.multiply_point(u1, curve.G)
    p2 = curve.multiply_point(u2, pk)
    res = curve.add_points(p1, p2)
    return r == res.x


###########################################
# DEBUG CODE: the following code is needed to very the correct functioning of the threshold signature generation
###########################################
'''
# Define the elliptic curve (SECP256k1)
curve = EllipticCurve(
    p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
    a=0x0,
    b=0x7,
    G=Point(
        x=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
        y=0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
    ),
    n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
    h=0x0,
)
# sepc key ##############################################################################
secret = "PUT HERE A VALID PRIVATE KEY"


# Number of shares to create
numnodes = 10

# Threshold
t = 7

# Share the secret
shares = share_secret(secret, numnodes, t, curve)
print(f"Shares: {shares}")

# Message to be signed
message = "Test message!"

# Generate partial signatures
R, partial_signatures = generate_partial_signatures(shares[:t], message, curve)
print(f"Partial Signatures: {partial_signatures}")

# Combine partial signatures
final_signature = combine_partial_signatures(R, partial_signatures, curve)
print(f"Final Signature: {final_signature}")

# Generate public key from secret
public_key = curve.multiply_point(secret, curve.G)

# Verify the final signature
is_valid = verify_signature(public_key, message, final_signature, curve)
print(f"Is the final signature valid? {is_valid}")
'''
