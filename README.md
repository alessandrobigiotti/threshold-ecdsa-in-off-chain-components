# Threshold ECDSA in Off-Chain Components to Manage Inter-chain Transactions

This repository contains a library for elliptic curve operations (*EllipticCurveMaths.sol*) which is intended to be applicable to generic Weierstrass elliptic curves. The library operations are used by the *VerifyThresholdECDSA.sol* smart contract to verify an ECDSA-based threshold signature from an off-chain component. The threshold signature is used by off-chain components to manage inter-chain transactions and must be validated within a specific smart contact.


Enabling verification of a digital signature on blockchain coming from an off-chain component can open up numerous applications. This approach can be applied in all those contexts that involve an on-chain resource managed by a series of off-chain nodes and shared with users present in the blockchain.

The following picture shows the use case examined and the latency performance of the *VerifyThresholdECDSA* smart contract obtained on differnt blockchain networks:
![alt text](https://github.com/alessandrobigiotti/threshold-ecdsa-in-off-chain-components/blob/main/img/img1.png)

## Optimised Elliptic Curve Operations

The Table shows the gas consumed by individual operations on each elliptic curve indicated. The performance of the proposed library, *EllipticCurveMath.sol*, was compared to other open source implementations found on Github. The symbol "-" means "Not applicable" and the symbol X means "Operation not provided".

|Elliptic Curve|   Operation   |[MerklePlant](https://github.com/verklegarden/crysol/blob/main/src/onchain/secp256k1/Secp256k1Arithmetic.sol)|[Renaud Dubois](https://github.com/rdubois-crypto/FreshCryptoLib/blob/master/solidity/src/FCL_elliptic.sol)|[Witenet Foundation](https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol)|*EllipticCurveMath.sol*|
| :---------------- | :---------------: | ----: | ----: | ----: | ----: |
|secp256k1|$k^{−1}$ (mod $q$)|3644|-| 66193| 2763 |
|secp256k1|$2 \cdot P$|X|-|2534|1887|
|secp256k1|$P_1+P_2$|4148|-|4679|3353|
|secp256k1|$k \cdot G$|532791|-|619588|229223|
|secp256k1|$u_1 \cdot G + u_2 \cdot P_k$|X|-|X|286764|
|secp256r1|$k^{−1}$ (mod $q$)|-|2642|64285|2811|
|secp256r1|$2 \cdot P$|-|2346|2552|2248|
|secp256r1|$P_1+P_2$|-|3902|4691|3833|
|secp256r1|$k \cdot G$|-|X|625377|384084|
|secp256r1|$u_1 \cdot G + u_2 \cdot P_k$|-|347658|X|433946|
|brainpoolp256r1|$k^{−1}$ (mod $q$)|-|-|65358|2850|
|brainpoolp256r1|$2 \cdot P$|-|-|2563|2439|
|brainpoolp256r1|$P_1+P_2$|-|-|4710|4155|
|brainpoolp256r1|$k \cdot G$|-|-|628592|477842|
|brainpoolp256r1|$u_1 \cdot G + u_2 \cdot P_k$|-|-|X|564917|


To find other projects implementing elliptic curve operations on Solidity, a search was conducted using the query strings: "*Solidity ECDSA*" (34 rsults), and "*Solidity Elliptic Curve*" (18 results), 2 repositories were contained in both the researches for a total of 50 repositories. The criterion for filtering the repositories found is based on the constraints: $c.1.$ Solidity version $>=$ 0.8.0 and $c.2.$ provide implementation for generic operations over Weierstrass elliptic curves. Using the filtering criterion: 22 repositories were discarded as they implement [Openzeppelin ECDSA](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/cryptography/ECDSA.sol) for EIP-1271 ; 10 repositories were discarded for outdated solidity version; 12 repositories do not implement ECDSA in Solidity; 1 repository was discarded as support only Edward curves. The remaining repositories, [Renaud Dubois](https://github.com/rdubois-crypto/FreshCryptoLib/blob/master/solidity/src/FCL_elliptic.sol) provides an implementation compatible only with secp256r1 curve (known as NIST P-256 or prime256v1), [MerklePlant](https://github.com/verklegarden/crysol/blob/main/src/onchain/secp256k1/Secp256k1Arithmetic.sol) is compatible only with secp256k1 curve. The 3 remaining repositories make use of the implementation of elliptic curve provided by [Witenet Foundation](https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol). It seems that there are no other libraries in the literature that implement operations on elliptic curves.

The goal of the library is to be applicable on various Weierstrass Elliptic curves, and at the same time save as much gas as possible. The metrics shown in the table indicate the average gas consumed on 250 transactions carried out on a blockchain implemented with [Hyperledger Besu](https://www.hyperledger.org/projects/besu), configured as follows: five validator nodes, PoA consensus algorithm based on IBFT 2.0, block generation time of 2 seconds, 2GB EVM stack, gas-free (maximum gas limit per block).

The operations indicated mean: $k^{-1}$ (mod $q$) the inverse in modulus of a number greater than 250 bits, where $q$ is the order of the finite field $F_q$; $2 \cdot P$ is the calculation of double a point; $P_1+P_2$ is the point addition; $k \cdot G$ is the scalar multiplication between a value $k$ larger than 250bits and the generator $G$ of the specific curve; $u_1 \cdot G + u_2 \cdot P_k$ is the sum of two scalar product, conducted using the interleaved scalar multiplication algorithm, where both $u_1$ and $u_2$ are larger than 250 bits, $G$ is the generator of the curve and $P_k$ is a valid public key.

### Optimisation made
To improve performance compared to the libraries [MerklePlant](https://github.com/verklegarden/crysol/blob/main/src/onchain/secp256k1/Secp256k1Arithmetic.sol) and [Witenet Foundation](https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol), a series of optimizations have been made compared to existing implementations. In particular:
- Introduction of *Fermat's little theorem* for computing the inverse modulus $q$, where $q$ is the order of the finite field $F_q$. This optimization is applicable only to operations carried out modulus $q$, while for operations within the Abelian group $G_p$ the extended Euclid algorithm must be used since there is no guarantee that the order $p$ of the group $G$ is prime.
- Fixed the error of the function for the addition between two points, adding the check if the points are equal. In this way the function for the addition of two points can be used within iterative processes, without the process breaking if the points considered become equal (This was left by the author of [Witenet Foundation](https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol) in the comments).
- Optimised the functions for calculating the addition of points and for calculating the double of a point. The functions for calculating the addition of points and the double of a point do not use any data structures, arrays, structs or anything else. They are all based on state variables and the functions implemented are all in assembly. This drastically reduces gas consumption, especially in iterative functions.
- Introduction of the interleaved scalar product to speed up the calculation of the sum of scalar products. This is the core optimisation made. The last verification step of verifying an ECDSA-based signature involves the sum of two scalar products, therefore the introduction of the Strauss-Shamir's trick for the calculation drastically reduces gas consumption. To further optimise the function, a crafty implementation of the sum of two points is provided, using a subroutine written in assembly (i.e., a function into a function) which for the calculation of the sum of two points in Jacobian coordinates halves the calculations necessary for update the z coordinate (see function *addPointAssTrick*)




## Project Structure

The project contains the smart contracts used for testing. It is structured according to the best practice adopted by [nodejs](https://nodejs.org/en) and the deployment of the smart contracts was carried out via [truffle](https://archive.trufflesuite.com/docs/truffle/quickstart/).

All smart contracts are located under the ```contract/appContracts``` folder. In particular:
- *CompareECC.sol*: Contains calls to other smart contracts that implement generic operations on elliptic curves. This smart contract allows you to evaluate the gas consumed by the proposed library (EllipticCurveMaths.sol) compared to libraries found in literatures. In particular, the implementations of
[Witenet Foundation](https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol),
[Renaud Dubois](https://github.com/rdubois-crypto/FreshCryptoLib/blob/master/solidity/src/FCL_elliptic.sol) and [MerklePlant](https://github.com/verklegarden/crysol/blob/main/src/onchain/secp256k1/Secp256k1Arithmetic.sol).

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
