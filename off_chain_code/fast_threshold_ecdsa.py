import sys
sys.path.insert(1, '../threshold-ecdsa-in-off-chain-components/off_chain_code')
import random
import secrets
import hashlib
from web3 import Web3
from dataclasses import dataclass
from typing import Optional, List, Tuple
from elliptic_curve_operations import Point, EllipticCurve, ecdsa_sign, ecdsa_verify
from shamir_secret_sharing import generate_polynomial, evaluate_polynomial, share_secret, reconstruct_secret, lagrange_coefficient


# Function to sign a message
def partial_ecdsa_sign(sk, hash, k, curve):
    hash_int = int.from_bytes(hash, "big")
    p = curve.multiply_point(k, curve.G)
    if not curve.is_point_on_curve(p):
        return None
    r = p.x
    invk = pow(k, -1, curve.n)
    ad = (sk * r) % curve.n
    sum_m = (hash_int + ad) % curve.n
    s = (invk * sum_m) % curve.n

    return (r, s)

# Verify individual public keys
def verify_individual_public_keys(shares, public_keys, curve):
    for i, share in enumerate(shares):
        expected_pub_key = curve.multiply_point(share[1], curve.G)
        if public_keys[i] != expected_pub_key:
            return False
    return True

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

# Elliptic Curve parameters for secp256k1
q = curve.n
G = curve.G

# Example secret (private key)
secret = secrets.randbelow(q)
t = 7
n = 10
ids = list(range(1, n + 1))

# Generate shares
shares = share_secret(secret, n, t, curve)
print("Shares:", shares)

# Compute individual public keys
public_keys = [curve.multiply_point(share[1], G) for share in shares]
print("Public keys:", public_keys)

ids_signers = random.sample(ids, t)

rec_sk = 0
for index in ids_sign:
    rec_sk = (rec_sk + (lagrange_coefficient(index, ids_sign, curve) * shares[index-1][1]) % curve.n) % curve.n

assert rec_sk == secret

global_pk = curve.multiply_point(secret, curve.G)

rec_pk = Point()
for index in ids_sign:
    rec_pk = curve.add_points(rec_pk, curve.multiply_point(lagrange_coefficient(index, ids_sign, curve), public_keys[index-1]))

assert global_pk.x == rec_pk.x and global_pk.y == rec_pk.y

hash = Web3.solidity_keccak(['string'], ['Hello Blockchain!'])

nonces = [random.randrange(1, q) for _ in range(n)]

nonce_commitments = []
for i in range(n):
    nonce_commitments.append(curve.multiply_point(nonces[i], curve.G))

combined_nonce = Point()
for index in ids_signers:
    combined_nonce = curve.add_points(combined_nonce, nonce_commitments[index-1])

k = sum(s for s in nonces) % curve.n


z = int.from_bytes(hash, "big")

partial_signatures = []
for index in ids_signers:
    partial_signatures.append(partial_ecdsa_sign(shares[index-1][1], hash, k, curve))

r = partial_signatures[0][0]
s = 0
for i, index in enumerate(ids_signers):
    s = s + lagrange_coefficient(index, ids_signers, curve)*partial_signatures[i][1]


sign = (r, s)

ecdsa_verify(global_pk, hash, sign, curve)
