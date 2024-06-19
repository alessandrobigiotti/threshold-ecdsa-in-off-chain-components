import sys
sys.path.insert(1, '../threshold-ecdsa-in-off-chain-components/off_chain_code')
import os
import json
import random
import time
import string
import secrets
import traceback
import pandas as pd
import matplotlib as plt
from web3 import Web3
from web3.middleware import geth_poa_middleware
from shamir_secret_sharing import share_secret, reconstruct_secret
from elliptic_curve_operations import Point, EllipticCurve, ecdsa_sign
import config

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def key_gen():

########################################################
# SET UP THE ELLIPTIC CURVE AND THE OFF-CHAIN PROPERTIES
########################################################
# Define the Elliptic Curve [secp256k1]
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
sk = secrets.randbelow(curve.n)
n = 10
t = 7


###############################################################
# Specify the blockchain to interact with
###############################################################
network='besu_1'
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

###########################################################################
# Generate the shares and the public keys for every party
###########################################################################
pk = curve.multiply_point(sk, curve.G)
pk
shares = share_secret(sk, n, t, curve)

transactions_data = []

for i in range(250):
    print("Execution number: ", i)
    indices = sorted(random.sample(range(len(shares)), t))
    random_subset = [shares[i] for i in indices]
    rec_secret = reconstruct_secret(random_subset, t, curve.p)
    virtual_nonce = verify_contract.functions.getNonce().call({"from": account.address})
    virtual_nonce = virtual_nonce + 1
    val1 = secrets.randbelow(curve.p)
    val2 = secrets.randbelow(curve.p)
    str_val1 = get_random_string(10)
    hash = Web3.solidity_keccak(['uint256', 'uint256', 'string', 'address', 'uint256'], [val1, val2, str_val1, account.address, virtual_nonce])
    sign = ecdsa_sign(rec_secret, hash, curve)

    current_gas_price = w3.eth.gas_price
    estimated_gas = verify_contract.functions.verifyECDSA(virtual_nonce, val1, val2, str_val1, sign[0], sign[1]).estimate_gas({'from': account.address})

    raw_transaction = verify_contract.functions.verifyECDSA(virtual_nonce, val1, val2, str_val1, sign[0], sign[1]).build_transaction({
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

df = pd.DataFrame(transactions_data)
df.to_csv("verify_threshold_statistics.csv")
