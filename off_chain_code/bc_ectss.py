import sys
sys.path.insert(1, '../threshold-ecdsa-in-off-chain-components/off_chain_code')
from web3 import Web3
from elliptic_curve_operations import EllipticCurve, Point, ecdsa_sign, ecdsa_verify
from shamir_secret_sharing import generate_polynomial, evaluate_polynomial, share_secret, lagrange_coefficient
from typing import List, Tuple
import hashlib
import secrets
# Define your elliptic curve
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


def verify_secret_share(s_ij: int, eta_ij: Point, eta_i: List[Point], id_j: int, curve: EllipticCurve) -> bool:
    lhs = curve.multiply_point(s_ij, curve.G)
    rhs = Point()
    for mu, eta_i_mu in enumerate(eta_i):
        rhs = curve.add_points(rhs, curve.multiply_point((id_j ** mu)%curve.n, eta_i_mu))
    return lhs == rhs

# Key generation function
def key_gen(n: int, t: int, curve: EllipticCurve) -> Tuple[List[int], List[Point], int, Point]:
    q = curve.n
    p = curve.p
    nodes = list(range(1, n + 1))
    private_shares = []
    public_shares = []

    for i in nodes:
        secret = secrets.randbelow(curve.n)
        poly = generate_polynomial(secret, t, q)
        si = [evaluate_polynomial(poly, j, q) for j in nodes]
        private_shares.append(si)
        public_shares.append([curve.multiply_point(s, curve.G) for s in si])

    sk = [sum(si) % q for si in zip(*private_shares)]
    pk = [curve.multiply_point(s, curve.G) for s in sk]
    group_private_key = sum(poly[0] for poly in private_shares) % p

    group_public_key = curve.multiply_point(group_private_key, curve.G)

    return sk, pk, group_private_key, group_public_key


# Function to hash a message
def hash_message(message: str) -> int:
    # Use SHA-256 hash function for hashing the message
    hash_digest = hashlib.sha256(message.encode()).digest()
    return int.from_bytes(hash_digest, byteorder='big')


# Function to generate partial signature
def partial_signature(message: str, node_id: int, sk_i: int, ids: List[int], curve: EllipticCurve) -> Tuple[int, int, int]:
    q = curve.n
    p = curve.p
    # Step 1: Randomly select ki from finite field Z_q
    k_i = secrets.randbelow(q)
    # Step 2: Calculate ri = xi mod p, where (xi, yi) = kiG
    point = curve.multiply_point(k_i, curve.G)
    r_i = point.x % p
    if r_i == 0:
        return partial_signature(message, node_id, sk_i, ids, curve)  # Retry if ri is 0
    # Step 3: Calculate message digest e = H(m)
    e = hash_message(message)

    # Step 4: Randomly select (alpha_i, beta_i) such that ki = alpha_i * ri + beta_i * m
    alpha_i = secrets.randbelow(q)
    beta_i = ((k_i - alpha_i * r_i)%q * pow(e, -1, q)) % q
    # Calculate Lagrange interpolation coefficient chi_i
    chi_i = lagrange_coefficient(node_id - 1, ids, q)
    # Calculate li = alpha_i * ri + e * chi_i * SK_i
    l_i = (alpha_i * r_i + e * chi_i * sk_i) % q

    # Partial signature is (ri, li, beta_i)
    partial_sig = (r_i, l_i, beta_i)

    if (k_i != (alpha_i * r_i + beta_i * e)%q):
        return false

    return partial_sig

# Function to verify a partial signature
def verify_partial_signature(r_i: int, l_i: int, beta_i: int, message: str, public_key: Point, node_id: int, ids: List[int], curve: EllipticCurve) -> bool:
    q = curve.n
    p = curve.p
    e = hash_message(message)
    chi_i = lagrange_coefficient(node_id - 1, ids, q)
    gamma_i = (l_i + beta_i * e) % q

    # Calculate (x'_i, y'_i) = gamma_i * G - e * chi_i * PK_i
    point_gamma = curve.multiply_point(gamma_i, curve.G)
    point_echi_pk = curve.multiply_point((e * chi_i)%q, public_key)
    #point_echi_pk = curve.multiply_point(e%q, public_key)
    point_echi_pk_neg = Point(point_echi_pk.x, -point_echi_pk.y % p)
    point_combined = curve.add_points(point_gamma, point_echi_pk_neg)
    v_i = point_combined.x % p

    return v_i == r_i

def combine_partial_signatures(partial_sigs: List[Tuple[int, int, int]], message: str, ids: List[int], public_keys: List[Point], curve: EllipticCurve) -> Tuple[int, int, int]:
    q = curve.n
    p = curve.p
    e = hash_message(message)

    r_sum = 0
    l_sum = 0
    beta_sum = 0

    for i, (r_i, l_i, beta_i) in enumerate(partial_sigs):
        pk_i = public_keys[i]
        if not verify_partial_signature(r_i, l_i, beta_i, message, pk_i, i + 1, ids, curve):
            raise ValueError(f"Invalid partial signature from node {ids[i]}")

        r_sum = (r_sum + r_i) % q
        l_sum = (l_sum + l_i) % q
        beta_sum = (beta_sum + beta_i) % q

    threshold_signature = (r_sum, l_sum, beta_sum)
    return threshold_signature

# Function to verify the threshold signature
def verify_threshold_signature(threshold_sig: Tuple[int, int, int], message: str, group_public_key: Point, curve: EllipticCurve) -> bool:
    r, l, beta = threshold_sig
    q = curve.n
    p = curve.p
    e = hash_message(message)

    gamma = (l + beta * e) % q

    gamma_point = curve.multiply_point(gamma, curve.G)
    eQ = curve.multiply_point(e, group_public_key)
    eQ_neg = Point(eQ.x, -eQ.y % p)
    combined_point = curve.add_points(gamma_point, eQ_neg)

    v = combined_point.x % p

    return r == v





"""
# Function to combine partial signatures into a threshold signature
def combine_partial_signatures(partial_sigs: List[Tuple[int, int, int]], message: str, ids: List[int], public_keys: List[Point], curve: EllipticCurve) -> Tuple[int, int, int]:
    q = curve.n
    p = curve.p
    e = hash_message(message)

    r_sum = 0
    l_sum = 0
    beta_sum = 0

    for i, (r_i, l_i, beta_i) in enumerate(partial_sigs):
        pk_i = public_keys[i]
        if not verify_partial_signature(r_i, l_i, beta_i, message, pk_i, i + 1, ids, curve):
            raise ValueError(f"Invalid partial signature from node {ids[i]}")

        r_sum = (r_sum + r_i) % q
        l_sum = (l_sum + l_i) % q
        beta_sum = (beta_sum + beta_i) % q

    threshold_signature = (r_sum, l_sum, beta_sum)
    return threshold_signature

# Function to verify the threshold signature
def verify_threshold_signature(threshold_sig: Tuple[int, int, int], message: str, group_public_key: Point, curve: EllipticCurve) -> bool:
    r, l, beta = threshold_sig
    q = curve.n
    p = curve.p
    e = hash_message(message)

    gamma = (l + beta * e) % p

    gamma_point = curve.multiply_point(gamma, curve.G)
    eQ = curve.multiply_point(e, group_public_key)
    eQ_neg = Point(eQ.x, -eQ.y % p)
    combined_point = curve.add_points(gamma_point, eQ_neg)

    v = combined_point.x % p

    return r == v

# Function to verify the threshold signature
def verify_threshold_signature2(threshold_sig: Tuple[int, int, int], message: str, group_public_key: Point, curve: EllipticCurve) -> bool:
    r, l, beta = threshold_sig
    q = curve.n
    p = curve.p
    e = hash_message(message)

    gamma = (l + beta * e) % p

    gamma_point = curve.multiply_point(gamma, curve.G)
    eQ = curve.multiply_point(e, group_public_key)
    eQ_neg = Point(eQ.x, -eQ.y % p)
    combined_point = curve.add_points(gamma_point, eQ_neg)

    v = combined_point.x % p

    return r == v
"""

"""
# Function to combine partial signatures into a threshold signature
def combine_partial_signatures(partial_sigs: List[Tuple[int, int, int]], message: str, ids: List[int], public_keys: List[Point], curve: EllipticCurve) -> Tuple[int, int, int]:
    q = curve.n
    p = curve.p
    e = hash_message(message)

    r_sum = 0
    l_sum = 0
    beta_sum = 0
    count = 0
    for i, sig in enumerate(partial_sigs):
        r_i, l_i, beta_i = sig
        if not verify_partial_signature(r_i, l_i, beta_i, message, public_keys[i], i+1, ids, curve):
            raise ValueError(f"Invalid partial signature from node {ids[i]}")

        r_sum = (r_sum + r_i) % q
        l_sum = (l_sum + l_i) % q
        beta_sum = (beta_sum + beta_i) % q

    threshold_signature = (r_sum, l_sum, beta_sum)
    return threshold_signature
"""

"""
def verify_threshold_signature(threshold_sig, message, pk, curve):
    q = curve.n
    p = curve.p
    e = hash_message(message)

    r, l, beta = threshold_sig

    gamma = (l + beta*e)%p
    g_point = curve.multiply_point(gamma, curve.G)
    e_point = curve.multiply_point(e, pk)

    final_p = curve.add_points(g_point, Point(e_point.x, -e_point.y % p))

    return r == final_p.x
"""
"""
# Function to verify the threshold signature
def verify_threshold_signature2(threshold_sig: Tuple[int, int, int], message: str, group_public_key: Point, curve: EllipticCurve) -> bool:
    r, l, beta = threshold_sig
    q = curve.n
    p = curve.p
    e = hash_message(message)

    # Calculate gamma
    gamma = (l + beta * e) % q

    # Calculate (x', y') = gamma * G - e * Q
    gamma_point = curve.multiply_point(gamma, curve.G)
    eQ = curve.multiply_point(e, group_public_key)
    eQ_neg = Point(eQ.x, -eQ.y % p)
    combined_point = curve.add_points(gamma_point, eQ_neg)

    # Calculate v = x' mod p
    v = combined_point.x % p

    # Check if r == v
    return r == v
"""
# Example usage
n = 5  # number of nodes
t = 3  # threshold
message = "Hello, blockchain!"

"""
private_keys, public_keys, group_private_key, group_public_key, group_public_key2 = key_gen(n, t, curve)
group_public_key
group_public_key2

print(f"Private Keys: {private_keys}")
print(f"Public Keys: {public_keys}")
print(f"Group Private Key: {group_private_key}")
print(f"Group Public Key: {group_public_key}")
print(f"Group Public Key: {group_public_key2}")

ids = list(range(1, n + 1))

partial_sigs = [partial_signature(message, i + 1, private_keys[i], ids, curve) for i in range(n)]
for i, (r_i, l_i, beta_i) in enumerate(partial_sigs):
    pk_i = public_keys[i]
    print(verify_partial_signature(r_i, l_i, beta_i, message, pk_i, i + 1, ids, curve))
threshold_sig = combine_partial_signatures(partial_sigs[:t], message, ids, public_keys, curve)

print(f"Threshold Signature: {threshold_sig}")

verify_threshold_signature(threshold_sig, message, group_public_key, curve)
"""
private_keys, public_keys, group_private_key, group_public_key, secret_shares, broadcast_values = key_gen(n, t, curve)
#private_keys, public_keys, group_private_key, group_public_key, secret_shares, broadcast_values = key_gen_old(n, t, curve)
private_keys

public_keys

group_private_key
group_public_key

ids = list(range(1, n + 1))

# Verify the secret shares
for i in range(n):
    for j in range(n):
        s_ij = secret_shares[i][j]
        eta_i = broadcast_values[i]
        id_j = ids[j]
        eta_ij = curve.multiply_point(s_ij, curve.G)
        assert verify_secret_share(s_ij, eta_ij, eta_i, id_j, curve), f"Share {s_ij} from Node {i+1} to Node {j+1} is invalid"

print("All secret shares are valid")
#private_keys, public_keys, group_private_key, group_public_key = key_gen(n, t, curve)

# Generate partial signatures
partial_sigs = [partial_signature(message, i + 1, private_keys[i], ids, curve) for i in range(t)]
partial_sigs

for i, (r_i, l_i, beta_i) in enumerate(partial_sigs):
    pk_i = public_keys[i]
    print(verify_partial_signature(r_i, l_i, beta_i, message, pk_i, i + 1, ids, curve))


# Combine partial signatures to create a threshold signature
threshold_sig = combine_partial_signatures(partial_sigs, message, ids, public_keys, curve)

print(f"Threshold Signature: {threshold_sig}")

# Verify the threshold signature
is_valid = verify_threshold_signature(threshold_sig, message, group_public_key, curve)
print(f"Threshold Signature Valid: {is_valid}")
