import sys
sys.path.insert(1, '../threshold-signature/src/python_threshold')
import os
import json
import traceback
import time
import secrets
import pandas as pd
import matplotlib.pyplot as plt
from web3 import Web3
from web3.middleware import geth_poa_middleware
from elliptic_curve_operations import EllipticCurve, Point, ecdsa_sign, ecdsa_verify
import config

################################################################################
# FILE DESCRIPTION:
# This file contains functions to compare the elliptic curve implementations found
# on Github against the proposed implementation.
# The comparison are conducted on a private Hyperledger Besu blockchain.
################################################################################

# Load the besu configuration from the file config.py
ws_besu = config.ws_besu
# Load the private key used to send transactions from config.py
private_key_besu = config.besu_pk

# Instantiate a Web3 calss to interact with the blockchain
w3 = Web3(Web3.WebsocketProvider(ws_besu[0]))
# Inject the middleware_onion
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
# load the account using the private key
account = w3.eth.account.from_key(private_key_besu)

# Load the json of the compiled contract CompareECC.sol and its address within the blockchain
path_compiled_compare_ecc = os.path.abspath('../threshold-signature/build/contracts/CompareECC.json')
path_address = os.path.abspath('../threshold-signature/contractAddresses/besu/addresses.json')

# load contract abi and bytecode
compare_contract = dict()
with open(path_compiled_compare_ecc, 'r') as json_file:
    compiled_contract = json.load(json_file)
    compare_contract['abi'] = compiled_contract['abi']
    compare_contract['bytecode'] = compiled_contract['bytecode']

# load verify_contract address
with open(path_address, 'r') as json_file:
    address_data = json.load(json_file)
    compare_contract['address'] = address_data['CompareECC']

# Load the contract from the blockchain
compare_contract = w3.eth.contract(abi=compare_contract['abi'], address=compare_contract['address'])
compare_contract.address

###############################################################################
# Be carefull, only our implementation and the implementation from Witenet Foundation
# allow the application of generic elliptic curve
# To test the MerklePlant repo use the secp256k1 curve
# To test the Doubois Renaud repo use the secp256r1 curve
###############################################################################
# Create the elliptic curve object
# Curve BRAINPOOLP256r1
curve = EllipticCurve(
    p =76884956397045344220809746629001649093037950200943055203735601445031516197751,
    a =56698187605326110043627228396178346077120614539475214109386828188763884139993,
    b =17577232497321838841075697789794520262950426058923084567046852300633325438902,
    G = Point(
        x =63243729749562333355292243550312970334778175571054726587095381623627144114786,
        y =38218615093753523893122277964030810387585405539772602581557831887485717997975
    ),
    n = 76884956397045344220809746629001649092737531784414529538755519063063536359079,
    h = 1
)

# BRAINPOOLP256r1 sk
sk = "PUT HERE A VALID PRIVATE KEY"
# Compute the public key from the private key
pk = curve.multiply_point(sk, curve.G)

# Repo1:
# https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol

# Repo2:
# https://github.com/rdubois-crypto/FreshCryptoLib/blob/master/solidity/src/FCL_elliptic.sol

# Repo3:
# https://github.com/pmerkleplant/crysol/blob/main/src/secp256k1/Secp256k1Arithmetic.sol
# https://github.com/pmerkleplant/crysol/blob/main/src/secp256k1/Secp256k1Arithmetic.sol


#########################################################################################
# INVERSE MODULE
# Test the gans consumption of the inverse module operation
#########################################################################################
for i in range(250):
    ski = secrets.randbelow(curve.p)
    raw_tx = compare_contract.functions.checkInverseBase(ski).build_transaction({
        'from':  account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        "gasPrice": 0
        # Additional fields like 'gas', 'value', etc., can be specified if necessary
    })

    signed_txn = w3.eth.account.sign_transaction(raw_tx, private_key=private_key_besu)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    receipt
    receipt.gasUsed - 21000
    transactions_data.append({
        'Repo1InvMod': receipt.gasUsed - 21000
    })

    # STATS ON Repo2 only (SECP256R1)
    # Mod Inverse
    raw_tx = compare_contract.functions.checkInverseFCC(ski).build_transaction({
        'from':  account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        "gasPrice": 0
    })
    signed_txn = w3.eth.account.sign_transaction(raw_tx, private_key=private_key_besu)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    receipt
    receipt.gasUsed - 21000
    transactions_data.append({
        'Repo2InvMod': receipt.gasUsed - 21000
    })

    # Stats on Repo3 only (SECP256K1)
    # Mod Inverse
    raw_tx = compare_contract.functions.checkInverseSecp256k1(ski).build_transaction({
        'from':  account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        "gasPrice": 0
        # Additional fields like 'gas', 'value', etc., can be specified if necessary
    })

    signed_txn = w3.eth.account.sign_transaction(raw_tx, private_key=private_key_besu)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    receipt
    receipt.gasUsed - 21000
    transactions_data.append({
        'Repo3InvMod': receipt.gasUsed - 21000
    })

    # STATS on proposal
    # Mod Inverse
    raw_tx = compare_contract.functions.checkInverseOpt(ski).build_transaction({
        'from':  account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        "gasPrice": 0
        # Additional fields like 'gas', 'value', etc., can be specified if necessary
    })

    signed_txn = w3.eth.account.sign_transaction(raw_tx, private_key=private_key_besu)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    receipt
    receipt.gasUsed - 21000
    transactions_data.append({
        'ProposedInvMod': receipt.gasUsed - 21000
    })

############################################################################################
# END MODULAR INVERSE
############################################################################################


############################################################################################
# START JACOBIAN DOUBLE
# Test the gas consumption of the double point operation in Jacobian Coordinates
############################################################################################
P = curve.add_points(curve.G, curve.G)
for i in range(250):
    # Generate a random point on the curve
    P = curve.add_points(P, curve.G)

    # prepare a raw transaction directed to the s.c.
    raw_tx = compare_contract.functions.checkJacobianDoubleNormal(P.x, P.y).build_transaction({
        'from':  account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        "gasPrice": 0
        # Additional fields like 'gas', 'value', etc., can be specified if necessary
    })

    signed_txn = w3.eth.account.sign_transaction(raw_tx, private_key=private_key_besu)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    receipt
    receipt.gasUsed - 21000
    transactions_data.append({
        'Repo1JacDouble': receipt.gasUsed - 21000
    })


    ############################################################################################
    # Double points
    # Repo2
    raw_tx = compare_contract.functions.checkJacobianDoubleFCC(P.x, P.y).build_transaction({
        'from':  account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        "gasPrice": 0
        # Additional fields like 'gas', 'value', etc., can be specified if necessary
    })

    signed_txn = w3.eth.account.sign_transaction(raw_tx, private_key=private_key_besu)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    receipt
    receipt.gasUsed - 21000
    transactions_data.append({
        'Repo2JacDouble': receipt.gasUsed - 21000
    })

    ############################################################################################
    # Jacobian Double
    # Opt propose
    raw_tx = compare_contract.functions.checkJacobianDoubleOpt(P.x, P.y).build_transaction({
        'from':  account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        "gasPrice": 0
        # Additional fields like 'gas', 'value', etc., can be specified if necessary
    })

    signed_txn = w3.eth.account.sign_transaction(raw_tx, private_key=private_key_besu)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    receipt
    receipt.gasUsed - 21000
    transactions_data.append({
        'ProposedJacDouble': receipt.gasUsed - 21000
    })

    # REPO 3 XXXXXXX
    # Not provided

############################################################################################
# END JACOBIAN DOUBLE
############################################################################################


############################################################################################
# START ADD POINT
############################################################################################

P1 = curve.add_points(curve.G, curve.G)
for i in range(250):
    P1 = curve.add_points(P1, curve.G)
    P2 = curve.add_points(P1, pk)

    raw_tx = compare_contract.functions.checkAddPointBase(P1.x, P1.y, P2.x, P2.y).build_transaction({
        'from':  account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        "gasPrice": 0
        # Additional fields like 'gas', 'value', etc., can be specified if necessary
    })

    signed_txn = w3.eth.account.sign_transaction(raw_tx, private_key=private_key_besu)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    receipt
    receipt.gasUsed - 21000
    transactions_data.append({
        'Repo1AddPoint': receipt.gasUsed - 21000
    })
    ############################################################################################################
    # Add points
    # Repo2

    raw_tx = compare_contract.functions.checkAddPointFCC(P1.x, P1.y, P2.x, P2.y).build_transaction({
        'from':  account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        "gasPrice": 0
        # Additional fields like 'gas', 'value', etc., can be specified if necessary
    })

    signed_txn = w3.eth.account.sign_transaction(raw_tx, private_key=private_key_besu)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    receipt
    receipt.gasUsed - 21000
    transactions_data.append({
        'Repo2AddPoint': receipt.gasUsed - 21000
    })

    ############################################################################################
    # Jacobian Add
    # Repo3
    raw_tx = compare_contract.functions.checkAddPointSECP256(P1.x, P1.y, P2.x, P2.y).build_transaction({
        'from':  account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        "gasPrice": 0
        # Additional fields like 'gas', 'value', etc., can be specified if necessary
    })

    signed_txn = w3.eth.account.sign_transaction(raw_tx, private_key=private_key_besu)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    receipt
    receipt.gasUsed - 21000
    transactions_data.append({
        'Repo3AddPoint': receipt.gasUsed - 21000
    })

    ############################################################################################
    # Jacobian Add
    # Proposed
    raw_tx = compare_contract.functions.checkAddPointOpt(P1.x, P1.y, P2.x, P2.y).build_transaction({
        'from':  account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        "gasPrice": 0
        # Additional fields like 'gas', 'value', etc., can be specified if necessary
    })

    signed_txn = w3.eth.account.sign_transaction(raw_tx, private_key=private_key_besu)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    receipt
    receipt.gasUsed - 21000
    transactions_data.append({
        'ProposedAddPoint': receipt.gasUsed - 21000
    })

###############################################################################################
# END ADD POINT
###############################################################################################


###############################################################################################
# START SCALAR MULT
###############################################################################################

###############################################################################################

for i in range(250):
    ski = secrets.randbelow(sk)
    raw_tx = compare_contract.functions.checkScalarMultiplication(ski, curve.G.x, curve.G.y).build_transaction({
        'from':  account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        "gasPrice": 0
        # Additional fields like 'gas', 'value', etc., can be specified if necessary
    })

    signed_txn = w3.eth.account.sign_transaction(raw_tx, private_key=private_key_besu)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    receipt
    receipt.gasUsed - 21000
    transactions_data.append({
        'Repo1Scalar': receipt.gasUsed - 21000
    })

    ########################### REPO 2
    # Not provided

###############################################################################################
    # scalar mul
    raw_tx = compare_contract.functions.checkScalrMulSecp256k1(ski, curve.G.x, curve.G.y).build_transaction({
        'from':  account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        "gasPrice": 0
        # Additional fields like 'gas', 'value', etc., can be specified if necessary
    })

    signed_txn = w3.eth.account.sign_transaction(raw_tx, private_key=private_key_besu)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    receipt
    receipt.gasUsed - 21000
    transactions_data.append({
        'Repo3Scalar': receipt.gasUsed - 21000
    })

    # scalar mul
    raw_tx = compare_contract.functions.checkScalarOptMultiplication(ski, curve.G.x, curve.G.y).build_transaction({
        'from':  account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        "gasPrice": 0
        # Additional fields like 'gas', 'value', etc., can be specified if necessary
    })

    signed_txn = w3.eth.account.sign_transaction(raw_tx, private_key=private_key_besu)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    receipt
    receipt.gasUsed - 21000
    transactions_data.append({
        'ProposedScalar': receipt.gasUsed - 21000
    })


#########################################################################################
# END SCALAR TESTS
#########################################################################################


############################################################################################
# START Strauss-Shamir's Trick
#############################################################################################

for i in range(250):
    sk1 = secrets.randbelow(sk)
    sk2 = secrets.randbelow(sk)

    raw_tx = compare_contract.functions.checkShamirTrickFCC(sk1, sk2, pk.x, pk.y).build_transaction({
        'from':  account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        "gasPrice": 0
        # Additional fields like 'gas', 'value', etc., can be specified if necessary
    })

    signed_txn = w3.eth.account.sign_transaction(raw_tx, private_key=private_key_besu)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    receipt
    receipt.gasUsed - 21000
    transactions_data.append({
        'Repo2Strauss': receipt.gasUsed - 21000
    })

    ###############################################################################################
    ###############################################################################################
    #   Shamir's trick
    #

    raw_tx = compare_contract.functions.checkShamirsTrickOpt(sk1, sk2, pk.x, pk.y).build_transaction({
        'from':  account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        "gasPrice": 0
        # Additional fields like 'gas', 'value', etc., can be specified if necessary
    })

    signed_txn = w3.eth.account.sign_transaction(raw_tx, private_key=private_key_besu)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    receiptistic
    receipt.gasUsed - 21000
    transactions_data.append({
        'ProposedStrauss': receipt.gasUsed - 21000
    })
#########################################################################################
#########################################################################################
#########################################################################################
df = pd.DataFrame(transactions_data)
df.to_csv("stats_comparisons")
