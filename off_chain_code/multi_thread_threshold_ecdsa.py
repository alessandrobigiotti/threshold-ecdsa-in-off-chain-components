import os
import sys
sys.path.insert(1, '../threshold-ecdsa-in-off-chain-components/off_chain_code')
import json
import secrets
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dataclasses import dataclass
from typing import Optional, List, Tuple
from elliptic_curve_operations import Point, EllipticCurve, ecdsa_sign, ecdsa_verify
from shamir_secret_sharing import generate_polynomial, evaluate_polynomial, share_secret, lagrange_coefficient
from threshold_ecdsa_utils import key_gen, partial_ecdsa_sign, combine_partial_signatures
import config
import pandas as pd
import threading
import random
import string
import time
###############################################
# Shared variables
###############################################
num_nodes = 10 # number of nodes
threshold = 7 # minimum threshold
hash = None # message to be signed
thread_lock = threading.Lock()  # Lock to synchronise access to hash_result
condition = threading.Condition()  # Condition variable to notify the primary thread
new_message_event = threading.Event()  # Event to signal secondary threads to start processing
active_threads = [False] * (threshold)  # List to track which threads are active in each iteration
partial_signatures = [None] * (threshold) # List to track the partial signatures
barrier = threading.Barrier(threshold) # Barrier to sinchronise the threads actions
nonce_commitments = [] # Commitment of the nonce during threshold generation
ids_signers = [] # ID of the off-chain threads
transactions_data = [] # List of all transactions

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

class HashThread(threading.Thread):
    def __init__(self, index, share, public_key, curve):
        super().__init__()
        self.index = index
        self.share = share
        self.public_key = public_key
        self.curve = curve

    def run(self):
        global hash, hash_result, nonce_commitments, partial_sign, ids_signers

        while True:
            new_message_event.wait()  # Wait for a new message to process

            if hash is None:  # Exit signal
                break

            if active_threads[self.index]:  # Only process if this thread is selected
                # Compute the hash using message, public_secret, and random_secret
                nonce = secrets.randbelow(curve.n)

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

def primary_thread(global_pk, curve, w3, verify_contract, account):
    global hash, hash_result, active_threads, nonce_commitments, partial_signatures, ids_signers, transactions_data
    time.sleep(2)
    for i in range(250):  # Generate 10 messages
        # Generate a random message
        val1 = secrets.randbelow(curve.n)
        val2 = secrets.randbelow(curve.n)
        str_val1 = get_random_string(10)
        virtual_nonce = 10000

        hash = Web3.solidity_keccak(['uint256', 'uint256', 'string', 'address', 'uint256'], [val1, val2, str_val1, account.address, virtual_nonce])
        # Reset hash_result for new round
        nonce_commitments = []
        partial_signatures = []
        ids_signers = []

        # Select a random subset of 4 threads
        selected_threads = random.sample(range(num_nodes-1), threshold)
        active_threads = [j in selected_threads for j in range(num_nodes-1)]

        # Signal secondary threads to start processing the new message
        new_message_event.set()

        # Wait for all selected secondary threads to complete
        with condition:
            while len(partial_signatures) != threshold:
                condition.wait()

        final_sign = combine_partial_signatures(partial_signatures, ids_signers, curve)
        print("Final signature: ", final_sign)

        ##################################################################
        # Verify the signature on-chain
        ##################################################################
        current_gas_price = w3.eth.gas_price
        estimated_gas = verify_contract.functions.verifyECDSA(virtual_nonce, val1, val2, str_val1, final_sign[0], final_sign[1]).estimate_gas({'from': account.address})

        raw_transaction = verify_contract.functions.verifyECDSA(virtual_nonce, val1, val2, str_val1, final_sign[0], final_sign[1]).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gasPrice": current_gas_price,
            "gas": estimated_gas+1000
        })

        signed_tx = w3.eth.account.sign_transaction(raw_transaction, private_key=prv_key)
        submission_time = int(time.time())
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        txn_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        block = w3.eth.get_block(txn_receipt.blockNumber)
        validation_time = block.timestamp
        slippage = validation_time - submission_time
        transactions_data.append({
            'tx_number': i+1,
            'tx_hash': tx_hash,
            'block': txn_receipt.blockNumber,
            'submission_time': submission_time,
            'validation_time': validation_time,
            'slippage': slippage,
            'gas_used': txn_receipt.gasUsed
        })
        time.sleep(validation_time%7+5)
        print("Sleep for: ", validation_time%7+5)

    # Signal threads to exit
    message = None
    new_message_event.set()  # Signal the threads to exit

    df = pd.DataFrame(transactions_data)
    df.to_csv("verify_threshold_statistics.csv")

if __name__ == '__main__':
    ###############################################################
    # Specify the blockchain to interact with
    ###############################################################
    network='besu'
    path_compiled_verify_threshold = os.path.abspath('../threshold-ecdsa-in-off-chain-components/build/contracts/VerifyThresholdECDSA.json')
    path_address = os.path.abspath('../threshold-ecdsa-in-off-chain-components/contractAddresses/'+network+'/addresses.json')

    #websoket = config.ws_besu
    websocket = config.ws_besu
    #prv_key = config.besu_pk
    prv_key = config.besu_pk

    ################################################################
    # NOTA: For blockchains that use PoA-type consensus algorithms,
    # it is necessary to inject the middleware_onion to avoid errors
    # when reading the blocks
    ################################################################
    w3 = Web3(Web3.WebsocketProvider(websocket[0]))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    account = w3.eth.account.from_key(prv_key)
    ##########################################################################
    # load contract abi and bytecode
    verify_contract = dict()
    with open(path_compiled_verify_threshold, 'r') as json_file:
        compiled_contract = json.load(json_file)
        verify_contract['abi'] = compiled_contract['abi']
        verify_contract['bytecode'] = compiled_contract['bytecode']

    # load verify_contract address
    with open(path_address, 'r') as json_file:
        address_data = json.load(json_file)
        verify_contract['address'] = address_data['VerifyThreshold']

    verify_contract = w3.eth.contract(abi=verify_contract['abi'], address=verify_contract['address'])

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

    ##############################################################################
    # Update the public key stored on the verify smart contract
    ##############################################################################
    current_gas_price = w3.eth.gas_price
    estimated_gas = verify_contract.functions.updatePublicKey(global_pk.x, global_pk.y).estimate_gas({'from': account.address})
    estimated_gas
    raw_tx = verify_contract.functions.updatePublicKey(global_pk.x, global_pk.y).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gasPrice": current_gas_price,
        "gas": estimated_gas+1000
    })
    signed_tx = w3.eth.account.sign_transaction(raw_tx, private_key=prv_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    # Create and start secondary threads
    threads = []

    for i in range(num_nodes-1):
        thread = HashThread(index=i, share=shares[i], public_key=public_keys[i], curve=curve)
        thread.start()
        threads.append(thread)

    # Start primary thread
    primary = threading.Thread(target=primary_thread, args=(global_pk, curve, w3, verify_contract, account))
    primary.start()
    primary.join()

    # Join all secondary threads
    for thread in threads:
        thread.join()
