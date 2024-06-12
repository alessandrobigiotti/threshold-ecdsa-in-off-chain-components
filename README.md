# Threshold ECDSA in Off-Chain Components to Manage Inter-chain Transactions

This repository contains a library for elliptic curve operations (*EllipticCurveMaths.sol*) which is intended to be applicable to generic Weierstrass elliptic curves. The library operations are used by the *VerifyThresholdECDSA.sol* smart contract to verify an ECDSA-based threshold signature from an off-chain component. The signature is needed by a blockchain user to enable him to initiate an inter-chain transaction and it is needed by the off-chain component to send a transaction to finalise an inter-chain transaction.

Enabling verification of a digital signature on blockchain coming from an off-chain component can open up numerous applications. This approach can be applied in all those contexts that involve an on-chain resource managed by a series of off-chain nodes and shared with users present in the blockchain.

The following picture shows the use case examined and the latency performance of the *VerifyThresholdECDSA* smart contract obtained on differnt blockchain networks:
![alt text](https://github.com/alessandrobigiotti/threshold-ecdsa-in-off-chain-components/blob/main/img/img.png)

## Optimised Elliptic Curve Operations

Table 1 shows the gas consumed by each operation needed for the threshold signature verification.
<p align="center">
<img src="https://github.com/alessandrobigiotti/threshold-ecdsa-in-off-chain-components/blob/main/img/gastable.png" alt="Gas consumption" style="width:65%; border:0;">
</p>

The goal of the *EllipticCurveMaths.sol* library is to minimise the gas consumed and allow the application of any Weierstrass elliptic curve. To this end, research was carried out on open source projects on github to understand the state of the art from an implementation point of view and evaluate any optimisations. The repositories considered had to meet the following requirements:

- $`C.1:`$ the Solidity version $`\geq`$ 0.8.0
- $`C.2:`$ the repository provides the implementation for generic operations over Weierstrass elliptic curves



## Project Structure

The project contains the smart contracts used for testing. It is structured according to the best practice adopted by [nodejs](https://nodejs.org/en) and the deployment of the smart contracts was carried out via [truffle](https://archive.trufflesuite.com/docs/truffle/quickstart/).

All smart contracts are located under the ```contract/appContracts``` folder. In particular:
- *CompareECC.sol*: Contains calls to other smart contracts that implement generic operations on elliptic curves. This smart contract allows you to evaluate the gas consumed by the proposed library (EllipticCurveMaths.sol) compared to libraries found in literatures. In particular, the implementations of
[Witenet Foundation](https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol),
[Renaud Dubois](https://github.com/rdubois-crypto/FreshCryptoLib/blob/master/solidity/src/FCL_elliptic.sol) and [MerklePlant](https://github.com/pmerkleplant/crysol/blob/main/src/secp256k1/Secp256k1Arithmetic.sol).

- *EllipticCurveMaths.sol*: Contains the proposed implementation. The library aims to be applicable to any Weierstrass elliptic curve and to save as much gas as possible for operations.

- *VerifyThresholdECDSA.sol*: This smart contract aims to verify an ECDSA-based digital signature that comes from an off-chain component. To do so, this smart contract has to reconstruct the message provided by the user, calculate its hash and verify the signature using the global public key.

## Deploy Configuration

To deploy and interact with smart contracts it is necessary to install the necessary node packages. The packages configuration is contained within the ```package.json``` file. To install the necessary packages it is sufficient to type from the root folder:
```
$ npm install
```
Once the packages are installed it is possible to deploy and interact with the smart contracts.

The Solidity compiler and blockchain configuration is found in the ```truffle-config.js``` file. In order to correctly compile and deploy the smart contracts it is necessary:
1. Verify the imports in the smart contract *CompareECC.sol*. If the imports from the other repositories doesn't work, try downloading the smart contracts and importing them locally.
2. Configure ```truffle-config.js``` appropriately. It involves the creation of the API-KEY to interact with the testnet blockchains and specify the local Besu blockchain. It can be done following the description within the file itself.

Once the setup is completed it is possible to compile the smart contracts by typing from the root folder:
```
truffle compile
```

Then, deploy the smart contracts:
```
truffle migrate --reset --network=<network-name>
```
Specifying the name of the specific network.

***NOTICE:*** If you want to test the smart contracts on [Remix IDE](https://remix.ethereum.org/) it is mandatory to enable the optimiser under advanced settings!

## Disclaimer
THIS SOFTWARE IS PROVIDED AS IS WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.
