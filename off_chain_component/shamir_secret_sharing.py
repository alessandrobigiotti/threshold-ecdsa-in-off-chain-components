import sys
sys.path.insert(1, '../threshold-ecdsa-in-off-chain-components/off_chain_component')
from web3 import Web3
from elliptic_curve_operations import EllipticCurve, Point, ecdsa_sign, ecdsa_verify
import hashlib
import random
import secrets

# Function to generate a generic polynomial
def generate_random_polynomial(t, curve):
    coefficients = [random.randint(1, curve.p-1) for _ in range (t)]

    def polynomial(x):
        result = 0
        for i, coef in enumerate(coefficients):
            result += coef * (x ** i)
        return result

    return coefficients, polynomial

# Function to generate a random polynomial of degree t-1
def generate_polynomial(secret, t, curve):
    coefficients = [secret]
    for _ in range(t - 1):
        coefficients.append(secrets.randbelow(curve.p))
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
        y = evaluate_polynomial(coefficients, x, curve.p)
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



###########################################
# DEBUG CODE: the following code is needed to very the correct functioning of the secret sharing
###########################################
'''
# Elliptic Curve
# SECP256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
a = 0
b = 7
G = Point(
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
)
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
h = 1
curve = EllipticCurve(p, a, b, G, n, h)

secret = "PUT HERE A VALID PRIVATE KEY"
# Define the parameters for sharing the secret
numnodes = 5  # Total number of parties
t = 3  # Number of parties needed to reconstruct the secret

shares = share_secret(secret, numnodes, t, curve)
shares
recombine_shares = [shares[0]] + [shares[3]] + [shares[4]]

rec_secret = reconstruct_secret(shares, t, curve.p)

print("Reconstruction result: ", rec_secret == secret)
'''
