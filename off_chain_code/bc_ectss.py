import sys
sys.path.insert(1, '../threshold-ecdsa-in-off-chain-components/off_chain_code')
from web3 import Web3
from elliptic_curve_operations import EllipticCurve, Point, ecdsa_sign, ecdsa_verify
from shamir_secret_sharing import lagrange_coefficient, share_secret, generate_polynomial, evaluate_polynomial
from typing import List, Tuple
import hashlib
import secrets

# Key generation function
def key_gen(n: int, t: int, curve: EllipticCurve) -> Tuple[List[int], List[Point], int, Point]:
    q = curve.n
    p = curve.p
    nodes_id = list(range(1, n + 1))

    f_coefficients = []
    mu_values = []
    broadcast_shares = []

    # Generate shares
    for node in nodes_id:
        f_i = generate_polynomial(secrets.randbelow(curve.n), t, curve)
        f_coefficients.append(f_i)

        mu_i = [curve.multiply_point(coeff, curve.G) for coeff in f_i]
        mu_values.append(mu_i)

        broadcast = dict()
        for ids in nodes_id:
            broadcast[ids] = evaluate_polynomial(f_i, ids, curve.n)
        broadcast_shares.append(broadcast)

    # Verify the shares
    for i in nodes_id:
        mu_i = mu_values[i-1]
        for j in nodes_id:
            s_ij = broadcast_shares[i-1][j]
            if not verify_share(j, mu_i, s_ij, curve):
                return None, None, None

    return f_coefficients, mu_values, broadcast_shares

# Verify if the shares are valid
def verify_share(idx_receiver, mu_values, share, curve):

    lhs = curve.multiply_point(share, curve.G)
    rhs = Point()
    for i, p in enumerate(mu_values):
        rhs = curve.add_points(rhs, curve.multiply_point(pow(idx_receiver, i, curve.n), p))
    if lhs.x == rhs.x and lhs.y == rhs.y:
        return True
    return False


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

# Example usage
n = 10  # number of nodes
t = 7   # threshold
message = "Hello, blockchain!"


f_coefficients, mu_values, broadcast_shares = key_gen(n, t, curve)

if f_coefficients != None and mu_values != None and broadcast_shares != None:
    print("All shares are valid!")


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
