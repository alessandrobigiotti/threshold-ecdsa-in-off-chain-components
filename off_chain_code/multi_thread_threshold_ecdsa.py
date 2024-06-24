import sys
sys.path.insert(1, '../threshold-ecdsa-in-off-chain-components/off_chain_code')
import random
import secrets
from web3 import Web3
from dataclasses import dataclass
from typing import Optional, List, Tuple
from elliptic_curve_operations import Point, EllipticCurve, ecdsa_sign, ecdsa_verify
from shamir_secret_sharing import generate_polynomial, evaluate_polynomial, share_secret, lagrange_coefficient
from threshold_ecdsa_utils import key_gen, partial_ecdsa_sign, combine_partial_signatures
import threading
import hashlib
import random
import string

# Shared variables
num_nodes = 10
threshold = 7
message = None
thread_lock = threading.Lock()  # Lock to synchronize access to hash_result
condition = threading.Condition()  # Condition variable to notify the primary thread
new_message_event = threading.Event()  # Event to signal secondary threads to start processing
active_threads = [False] * (threshold)  # List to track which threads are active in each iteration
partial_signatures = [None] * (threshold)
barrier = threading.Barrier(threshold)
nonce_commitments = []
ids_signers = []

def generate_random_message(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_secret(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class HashThread(threading.Thread):
    def __init__(self, index, share, public_key, curve):
        super().__init__()
        self.index = index
        self.share = share
        self.public_key = public_key
        self.curve = curve

    def run(self):
        global message, hash_result, nonce_commitments, partial_sign, ids_signers

        while True:
            new_message_event.wait()  # Wait for a new message to process

            if message is None:  # Exit signal
                break

            if active_threads[self.index]:  # Only process if this thread is selected
                # Compute the hash using message, public_secret, and random_secret
                hash = Web3.solidity_keccak(['string'], [message])
                nonce = random.randrange(1, curve.n)

                # Share the individual commitments with the other threads
                with thread_lock:
                    nonce_commitments.append((self.index+1, nonce))
                    #hash_result[self.index] = hash

                # Compute the global k and generate the partial signature
                barrier.wait()
                k = sum(s[1] for s in nonce_commitments) % self.curve.n

                partial_sign = partial_ecdsa_sign(self.share[1], hash, k, self.curve)
                with thread_lock:
                    partial_signatures.append((self.index+1, partial_sign))
                    ids_signers.append(self.index+1)

                with condition:
                    condition.notify()  # Notify the primary thread that computation is done

            new_message_event.clear()  # Reset the event for the next round

def primary_thread(global_pk, curve):
    global message, hash_result, active_threads, nonce_commitments, partial_signatures, ids_signers

    for _ in range(10):  # Generate 10 messages
        # Generate a random message
        message = generate_random_message()
        hash = Web3.solidity_keccak(['string'], [message])
        # Reset hash_result for new round
        nonce_commitments = []
        partial_signatures = []
        ids_signers = []

        # Select a random subset of 4 threads
        selected_threads = random.sample(range(num_nodes-1), threshold)
        active_threads = [i in selected_threads for i in range(num_nodes-1)]

        # Signal secondary threads to start processing the new message
        new_message_event.set()

        # Wait for all selected secondary threads to complete
        with condition:
            while len(partial_signatures) != threshold:
                condition.wait()

        final_sign = combine_partial_signatures(partial_signatures, ids_signers, curve)
        print("Final signature: ", final_sign)

        check = ecdsa_verify(global_pk, hash, final_sign, curve)
        print("Final Signture: ", check)
    # Signal threads to exit
    message = None
    new_message_event.set()  # Signal the threads to exit

if __name__ == "__main__":
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

    secret = secrets.randbelow(curve.n)
    shares, public_keys = key_gen(secret, num_nodes, threshold, curve)
    global_pk = curve.multiply_point(secret, curve.G)

    # Create and start secondary threads
    threads = []

    for i in range(num_nodes-1):
        random_secret = generate_random_secret()
        thread = HashThread(index=i, share=shares[i], public_key=public_keys[i], curve=curve)
        thread.start()
        threads.append(thread)

    # Start primary thread
    primary = threading.Thread(target=primary_thread, args=(global_pk, curve,))
    primary.start()
    primary.join()

    # Join all secondary threads
    for thread in threads:
        thread.join()
