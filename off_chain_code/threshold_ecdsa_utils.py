import sys
sys.path.insert(1, '../threshold-ecdsa-in-off-chain-components/off_chain_code')
import random
import secrets
import hashlib
from web3 import Web3
from dataclasses import dataclass
from typing import Optional, List, Tuple
from elliptic_curve_operations import Point, EllipticCurve, ecdsa_sign, ecdsa_verify
from shamir_secret_sharing import generate_polynomial, evaluate_polynomial, share_secret, lagrange_coefficient

# Function to verify is the shares are correctly generated
def verify_shares(secret, shares, n, threshold, curve):
    ids = list(range(1, n + 1))
    ids_signers = random.sample(ids, threshold)

    rec_sk = 0
    for index in ids_signers:
        rec_sk = (rec_sk + (lagrange_coefficient(index, ids_signers, curve) * shares[index-1][1]) % curve.n) % curve.n

    return rec_sk == secret

# Function to verify if the individual public keys are correctly generated
def verify_public_keys(public_keys, secret, n, threshold, curve):
    ids = list(range(1, n + 1))
    ids_signers = random.sample(ids, threshold)

    global_pk = curve.multiply_point(secret, curve.G)

    rec_pk = Point()
    for index in ids_signers:
        rec_pk = curve.add_points(rec_pk, curve.multiply_point(lagrange_coefficient(index, ids_signers, curve), public_keys[index-1]))

    return global_pk.x == rec_pk.x and global_pk.y == rec_pk.y

# Function to generate the individual shares and public keys
def key_gen(secret, num_nodes, threshold, curve):
    # Generate shares
    shares = share_secret(secret, num_nodes, threshold, curve)

    # Compute individual public keys
    public_keys = [curve.multiply_point(share[1], curve.G) for share in shares]

    if (verify_shares(secret, shares, num_nodes, threshold, curve) and verify_public_keys(public_keys, secret, num_nodes, threshold, curve)):
        return shares, public_keys

    return None, None

# Function used by a party to produce a partial signature
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

# Function used by the primary node to combine the partial signatures
def combine_partial_signatures(partial_signatures, ids_signers, curve):
    r = partial_signatures[0][1][0]
    s = 0
    for i, index in enumerate(ids_signers):
        s = s + lagrange_coefficient(partial_signatures[i][0], ids_signers, curve)*partial_signatures[i][1][1]

    return (r,s%curve.n)
