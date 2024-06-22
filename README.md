# Threshold ECDSA in Off-Chain Components to Manage Inter-chain Transactions

This repository contains a library for elliptic curve operations (*EllipticCurveMaths.sol*) which is intended to be applicable to generic Weierstrass elliptic curves. The library operations are used by the *VerifyThresholdECDSA.sol* smart contract to verify an ECDSA-based threshold signature from an off-chain component. The threshold signature is used by off-chain components to manage inter-chain transactions and must be validated within a specific smart contact.

## Optimised Elliptic Curve Operations

To find other projects implementing elliptic curve operations on Solidity, a search was conducted using the query strings: "*Solidity ECDSA*" (34 rsults), and "*Solidity Elliptic Curve*" (18 results), 2 repositories were contained in both the researches for a total of 50 repositories. The criterion for filtering the repositories found is based on the constraints: $c.1.$ Solidity version $>=$ 0.8.0 and $c.2.$ provide implementation for generic operations over Weierstrass elliptic curves. Using the filtering criterion: 22 repositories were discarded as they implement [Openzeppelin ECDSA](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/cryptography/ECDSA.sol) for EIP-1271 ; 10 repositories were discarded for outdated solidity version; 12 repositories do not implement ECDSA in Solidity; 1 repository was discarded as support only Edward curves. The remaining repositories, [Renaud Dubois](https://github.com/rdubois-crypto/FreshCryptoLib/blob/master/solidity/src/FCL_elliptic.sol) provides an implementation compatible only with secp256r1 curve (known as NIST P-256 or prime256v1), [MerklePlant](https://github.com/verklegarden/crysol/blob/main/src/onchain/secp256k1/Secp256k1Arithmetic.sol) is compatible only with secp256k1 curve. The 3 remaining repositories make use of the implementation of elliptic curve provided by [Witenet Foundation](https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol). It seems that there are no other libraries in the literature that implement operations on elliptic curves.

The goal of the proposed library *EllipticCurveMaths.sol* is to be applicable on various Weierstrass Elliptic curves, and, at the same time, save as much gas as possible. The metrics shown in the table indicate the average gas consumed on 250 transactions carried out on a blockchain implemented with [Hyperledger Besu](https://www.hyperledger.org/projects/besu), configured as follows: five validator nodes, PoA consensus algorithm based on IBFT 2.0, block generation time of 2 seconds, 2GB EVM stack, gas-free (maximum gas limit per block).

The Table shows the gas consumed by individual operations on each elliptic curve indicated. The performance of the proposed library, *EllipticCurveMath.sol*, was compared to other open source implementations found on Github. The symbol "-" means "Not applicable" and the symbol "X" means "Operation not provided".

The operations indicated mean: $k^{-1}$ (mod $q$) the inverse in modulus of a number greater than 250 bits, where $q$ is the order of the finite field $F_q$; $2 \cdot P$ is the calculation of double a point; $P_1+P_2$ is the point addition; $k \cdot G$ is the scalar multiplication between a value $k$ larger than 250bits and the generator $G$ of the specific curve; $u_1 \cdot G + u_2 \cdot P_k$ is the sum of two scalar product, conducted using the interleaved scalar multiplication algorithm, where both $u_1$ and $u_2$ are larger than 250 bits, $G$ is the generator of the curve and $P_k$ is a valid public key.

|Elliptic Curve|   Operation   |[MerklePlant](https://github.com/verklegarden/crysol/blob/main/src/onchain/secp256k1/Secp256k1Arithmetic.sol)|[Renaud Dubois](https://github.com/rdubois-crypto/FreshCryptoLib/blob/master/solidity/src/FCL_elliptic.sol)|[Witenet Foundation](https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol)|*EllipticCurveMaths.sol*|
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

### Optimisation made
To improve performance compared to the libraries [MerklePlant](https://github.com/verklegarden/crysol/blob/main/src/onchain/secp256k1/Secp256k1Arithmetic.sol) and [Witenet Foundation](https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol), a series of optimizations have been made compared to existing implementations. In particular:
- Introduction of *Fermat's little theorem* for computing the inverse modulus $q$ , where $q$ is the order of the finite field $F_q$ . This optimisation is applicable only to operations carried out modulus $q$, while for operations within the abelian group $G_p$ the extended Euclid algorithm must be used since there is no guarantee that the order $p$ of the group $G$ is prime.
- Fixed the error of the function for the addition between two points, adding the check if the points are equal. In this way the function for the addition of two points can be used within iterative processes, without the process breaking if the points considered become equal (This was left by the author of [Witenet Foundation](https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol) in the comments).
- Optimised the functions for calculating the addition of points and for calculating the double of a point. The functions for calculating the addition of points and the double of a point do not use any data structures, arrays, structs or anything else. They are all based on state variables and the functions implemented are all in assembly. This drastically reduces gas consumption, especially in iterative functions.
- Introduction of the interleaved scalar product to speed up the calculation of the sum of two scalar products. This is the main optimisation performed. The last ECDSA-based signature verification step involves the sum of two scalar products, so introducing the Strauss-Shamir's trick to the calculation dramatically reduces gas consumption. To further optimise the function, a crafty implementation of the sum of two points is provided, using a subroutine written in assembly (i.e. a function within a function) which for the calculation of the sum of two points in Jacobian coordinates halves the calculations necessary to update the z coordinate (see function *addPointAssTrick*)

Compared with [Renaud Dubois](https://github.com/rdubois-crypto/FreshCryptoLib/blob/master/solidity/src/FCL_elliptic.sol)' implementation, the proposed solution aims to be applicable to several Weierstrass Elliptic Curves defined in a finite field $F_q$. The authors were able to exploit some assumptions on the properties of the adopted curve (secp256r1) which allow saving some computations and some checks, saving further gas. To extend the applicability to any elliptic curve it is inevitable to sacrifice some gas.

## Project Structure

This section explains the project structure, the main folders and describes the files content. The project contains smart contracts to be deployed on a evm-based blockchain, and it is structured according to the best practice adopted by [nodejs](https://nodejs.org/en) and the deployment of the smart contracts was carried out via [truffle](https://archive.trufflesuite.com/docs/truffle/quickstart/). The interaction to smart contracts and the off-chain processes are implemented using python.

### On-Chain code

The folder contracts contain the smart contracts to compute the elliptic curve operations and to verify a threshold signature based on ECDSA. All smart contracts are located under the ```contract/appContracts``` folder. In particular:
- *CompareECC.sol*: Contains calls to other smart contracts that implement generic operations on elliptic curves. This smart contract allows you to evaluate the gas consumed by the proposed library (EllipticCurveMaths.sol) compared to libraries found in literatures. In particular, the implementations of Repo1: [Witenet Foundation](https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol), Repo2: [Renaud Dubois](https://github.com/rdubois-crypto/FreshCryptoLib/blob/master/solidity/src/FCL_elliptic.sol) and Repo3: [MerklePlant](https://github.com/verklegarden/crysol/blob/main/src/onchain/secp256k1/Secp256k1Arithmetic.sol).

- *EllipticCurveMaths.sol*: Contains the proposed implementation. The library aims to be applicable to any Weierstrass elliptic curve and to save as much gas as possible for operations. All functions are implemented using assembly low level instructions, and assembly soub routine. The main method is the interleaved scalar product aimed to streamline the sum of two scalar products needed to verify a threshold based ecdsa signature.

- *VerifyThresholdECDSA.sol*: This smart contract aims to verify an ECDSA-based digital signature that comes from an off-chain component. To do so, this smart contract has to reconstruct the message provided by the user, calculate its hash and verify the signature using the global public key.

- *Source* and *Target* smart contracts: TO FINISH...


### Off-chain code

The folder off_chain_code contains the process needed to interact with the deployed smart contracts and generate threshold signatures. In particular:

- *repositories_comparison.py*: this file contains calls to the various smart contracts tested for elliptic curve calculations: Repo1: [Witenet Foundation](https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol), Repo2: [Renaud Dubois](https://github.com/rdubois-crypto/FreshCryptoLib/blob/master/solidity/src/FCL_elliptic.sol) and Repo3: [MerklePlant](https://github.com/verklegarden/crysol/blob/main/src/onchain/secp256k1/Secp256k1Arithmetic.sol) and *EllipticCurveMaths.sol* in order to calculate their average gas consumption. For each operation of those shown in the table, 250 transactions are carried out and finally a csv is saved on which the metrics shown have been calculated.

- *elliptic_curve_operations.py*: contains the functions that implement the main operations on an elliptical curve, which are: addition of points, multiplication of points, negation of a point, and verification of belonging of a point to a certain curve. The ```Point``` and ```EllipticCurve``` objects used by the various off-chain processes are defined here.

- *shamir_secret_sharing.py*: contains functions to share a certain secret $sk$ among a set of $n$ parties. Specifically, the  following functions are implemented:
  - *lagrange_coefficient*: this function allows you to recover the Lagrange coefficient relating to a specific part $i$ in a share from a polynomial of degree $t-1$: $$\lambda_i = \prod_{\substack{1 \le j \le t \\ j \ne i}} \frac{-ID_j}{ID_i - ID_j}$$
  - *generate_polynomial*: this function allows you to create a polynomial $f(x)$ of degree $t-1$, such that the coefficient $a_0$ = $f(0)$ contains the secret $sk$ to be shared with $n$ parties: $$f(x) = a_0 + a_1 x + a_2 x^2 + \cdots + a_{t-1} x^{t-1}$$
  - *share_secret*: this function implements the Shamir's Secret Sharing algorithm and allows sharing a secret $sk$ between $n$ parties. Each part obtains a pair ($i$, $f$($i$)), where $i$ is the index of the part and $f(i)$ is the value of the polynomial generated by the previous function.

- *try_simple_threshold_ecdsa.py*: this function simulates an ECDSA-based threshold digital signature. The secp256k1 elliptic curve is used in the simulation, the number of nodes $n$ is 10 and the threshold $t$ is 7. The algorithm used involves the following steps:
  1. *Key Distribution*: select a random number $sk$ (mod $p$), i.e., the secret to share. Using the procedures implemented in the *shamir_secret_sharing.py* file, the secret is divided into $n$ shares of the type ($i$, $f$($i$)), where $f$ is a polynomial of degree ($t-1$ ) randomly generated where $f(0)$ = $sk$. Each node calculates its own public key $pk_i$ = $f(i)$ $\cdot$ $G$, where $G$ is the generator point of the curve.

  After generating the shares and public keys, the procedure verifies their correctness, that is: $$sk = \sum_{i=1}^{t} \lambda_i \cdot f(i)$$ where, $\lambda_i$ is the lagrange coefficient. Then verify that the global public key is calculated correctly: $$sk \cdot G = \sum_{i=0}^{t} \lambda_i \cdot pk_i$$, where, $pk_i$ are the individual public keys of the individual parties.

  If both equalities are verified, the sharing of the secret between the various parties has occurred correctly.

  2. *Partial Signatures*: each party selects a secret nonce $k_i$ and produces its commitment on the nonce by computing the point $R_i$ = $k_i$ $\cdot$ $G$. Once the commitments have been collected, the point $$R = (x', y') = \sum_{i=1}^{t} R_i$$ is calculated, then the value $x'$ is taken as the agreed parameter for the calculation of partial signatures.

  Once the value $k$ has been agreed upon, each party produces their partial signature as follows: $$s_i ​ = (m + r \cdot f(i))⋅k^{−1}\ \text{mod}\ q$$, where $m$ is the hash of the message to be signed, $k$ is the shared nonce used by the nodes to sign the message; $r$ = $x'$ is the $x$ coordinate of the point $R$.

  3. *Threshold Signature*: Once the partial signatures $s_i$ have been calculated, they must be combined to produce the threshold signature $\sigma$. The aggregation procedure works as follows:
    $$r = r_i \Longleftrightarrow r_i = r_j \forall s_i, s_j \wedge i \neq j$$

    $$s = \sum_{i=1}^{t} \lambda_i \cdot s_i$$

    $$\sigma = (r,s)$$

  4. *Threshold Verification*: The verification is performed using the standard ECDSA verification algorithm.

- *multi_threading_threshold_sign.py*: this file contains a multithreading application simulating the off-chain nodes implementing a threshold signature based on ECDSA. TO FINISH...

- *bc_ectss.py*: This file contains operations for constructing an ECDSA-based threshold signature that differs from the standard signature. The file contains the implementation of the *BC_ECTSS* algorithm proposed by the authors in the following [paper](https://www.sciencedirect.com/science/article/abs/pii/S2214212622001909). Specifically, here we refer to section 4 of the paper, where the authors propose a new threshold signature scheme based on ECDSA. Below is a description of the operations carried out: TO FINISH...

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

##

## Disclaimer
THIS SOFTWARE IS PROVIDED AS IS WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.
