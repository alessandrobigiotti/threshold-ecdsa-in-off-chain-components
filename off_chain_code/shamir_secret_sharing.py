import sys
sys.path.insert(1, '../threshold-ecdsa-in-off-chain-components/off_chain_code')
import random
import secrets
import hashlib
from web3 import Web3
from dataclasses import dataclass
from typing import Optional, List, Tuple
from elliptic_curve_operations import Point, EllipticCurve, ecdsa_sign, ecdsa_verify

# Function Lagrange coefficient
def lagrange_coefficient(i: int, index: List[int], curve):
    numerator = 1
    denominator = 1
    for j in index:
        if i != j:
            numerator = (numerator * (-j)) % curve.n
            denominator = (denominator * (i - j)) % curve.n

    return numerator * pow(denominator, -1, curve.n) % curve.n

# Function to generate a random polynomial of degree t-1
def generate_polynomial(secret, t, curve):
    coefficients = [secret]
    for _ in range(t - 1):
        coefficients.append(secrets.randbelow(curve.n))
    return coefficients

# Function to evaluate the polynomial at a given x
def evaluate_polynomial(coefficients, i, curve_order):
    result = 0
    for coeff in reversed(coefficients):
        result = (result * i + coeff) % curve_order
    return result

# Function to share the secret among n parties
def share_secret(secret, n, t, curve):
    coefficients = generate_polynomial(secret, t, curve)
    shares = []
    for i in range(1, n + 1):
        x = i
        y = evaluate_polynomial(coefficients, x, curve.n)
        shares.append((x, y))

    return shares

# Function to reconstruct the secret using t out of n shares
def reconstruct_secret(shares, t, curve_order):
    secret = 0
    for i in range(t):
        numerator = 1
        denominator = 1
        for j in range(t):
            if i != j:
                numerator = (numerator * (-shares[j][0])) % curve_order
                denominator = (denominator * (shares[i][0] - shares[j][0])) % curve_order
        lagrange_coefficient = numerator * pow(denominator, -1, curve_order) % curve_order
        secret = (secret + (lagrange_coefficient * shares[i][1]) % curve_order) % curve_order
    return secret



"""
# Define the elliptic curve parameters
curve = EllipticCurve(
    p=0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f,
    a=0,
    b=7,
    G=Point(
        x=55066263022277343669578718895168534326250603453777594175500187360389116729240,
        y=32670510020758816978083085130507043184471273380659243275938904335757337482424
    ),
    n=0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141,
    h=1
)
# Generate a random secret number
secret = secrets.randbelow(curve.n)
secret
# Define the parameters for sharing the secret
n = 5  # Total number of parties
t = 3  # Number of parties needed to reconstruct the secret

shares = share_secret(secret, n, t, curve)
shares
recombine_shares = [shares[0]] + [shares[1]] + [shares[2]]

rec_secret = reconstruct_secret(recombine_shares, t, curve.n)

print("Reconstruction result: ", rec_secret == secret)
lagrange_coefficient(1, [1,2,3], curve)
"""
