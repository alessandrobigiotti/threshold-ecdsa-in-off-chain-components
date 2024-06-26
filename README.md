# Threshold ECDSA in Off-Chain Components to Manage Inter-chain Transactions

The repository contains the code to implement an interoperability protocol between permissioned blockchains. Each blockchain has its own off-chain component that is responsible for regulating user activities and finalising inter-chain transactions. Currently the use case for synchronisation between two smart contracts resident on two different blockchains is provided. The idea of ​​the protocol and how inter-chain transactions are handled by off-chain components is illustrated in the following figure.
![alt text](https://github.com/alessandrobigiotti/threshold-ecdsa-in-off-chain-components/blob/main/img/img.png)

The protocol involves three transactions to finalise an inter-chain transaction, which are: 1st transaction on the *SourceSmartContract* which initiates an inter-chain transaction, 2nd transaction on the *TargetSmartContract* which executes an inter-chain transaction in the destination blockchain, 3rd transaction on the *SourceSmartContract* as a completion ack. The off-chain components do not use consensus protocols, but are based on an ECDSA-based threshold digital signature.

### Roadmap

The project is constantly evolving and involves the following steps:

- :ballot_box_with_check: Optimising operations for verifying an ECDSA-based digital signature on smart contracts

- :ballot_box_with_check: Design and development of interface smart contracts *SourceSmartContract* and *TargetSmartContract*

- :ballot_box_with_check: Procedures for generating and verifying a simple ECDSA threshold for off-chain processes

- :ballot_box_with_check: Introduction of multi threading processes for the generation of a threshold signature based on ECDSA

- :arrows_counterclockwise: Procedures for generating and verifying the threshold signature scheme proposed by the authors of [bc_ectss](https://www.sciencedirect.com/science/article/abs/pii/S2214212622001909)

- :white_square_button: Introduction of multi threading processes for the generation of a [bc_ectss](https://www.sciencedirect.com/science/article/abs/pii/S2214212622001909) threshold signature based on ECDSA

- :white_square_button: Connect multithreaded processes to their respective smart contacts of interconnected blockchains

- :white_square_button: Extend the use cases covered by the *SourceSmartContract* and the *TargetSmartContract*

- :white_square_button: Replace multi threading processes with a real peer-to-peer network

## Optimised Elliptic Curve Operations

To find other projects implementing elliptic curve operations on Solidity, a search was conducted on Github using the query strings: "*Solidity ECDSA*" (34 rsults), and "*Solidity Elliptic Curve*" (18 results), 2 repositories were contained in both the researches for a total of 50 repositories. The criterion for filtering the repositories found is based on the constraints: $c.1.$ Solidity version $\geq$ 0.8.0 and $c.2.$ provide implementation for generic operations over Weierstrass elliptic curves. Using the filtering criterion: 22 repositories were discarded as they implement [Openzeppelin ECDSA](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/cryptography/ECDSA.sol) for EIP-1271 ; 10 repositories were discarded for outdated solidity version; 12 repositories do not implement ECDSA in Solidity; 1 repository was discarded as support only Edward curves. The remaining repositories, [Renaud Dubois](https://github.com/rdubois-crypto/FreshCryptoLib/blob/master/solidity/src/FCL_elliptic.sol) provides an implementation compatible only with secp256r1 curve (known as NIST P-256 or prime256v1), [MerklePlant](https://github.com/verklegarden/crysol/blob/main/src/onchain/secp256k1/Secp256k1Arithmetic.sol) is compatible only with secp256k1 curve. The 3 remaining repositories make use of the implementation of elliptic curve provided by [Witenet Foundation](https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol). It seems that there are no other libraries in the literature that implement operations on elliptic curves.

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

To improve performance compared to the libraries [MerklePlant](https://github.com/verklegarden/crysol/blob/main/src/onchain/secp256k1/Secp256k1Arithmetic.sol) and [Witenet Foundation](https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol), a series of optimisations have been made compared to existing implementations. In particular:

- Introduction of *Fermat's little theorem* for computing the inverse modulus $q$ , where $q$ is the order of the finite field $F_q$ . This optimisation is applicable only to operations carried out modulus $q$, while for operations within the abelian group $G_p$ the extended Euclid algorithm must be used since there is no guarantee that the order $p$ of the group $G$ is prime.

- Fixed the error of the function for the addition between two points, adding the check if the points are equal. In this way the function for the addition of two points can be used within iterative processes, without the process breaking if the points considered become equal (This was left by the author of [Witenet Foundation](https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol) in the comments).

- Optimised the functions for calculating the addition of points and for calculating the double of a point. The functions for calculating the addition of points and the double of a point do not use any data structures, arrays, structs or anything else. They are all based on state variables and the functions implemented are all in assembly. This drastically reduces gas consumption, especially in iterative functions.

- Introduction of the interleaved scalar product to speed up the calculation of the sum of two scalar products. This is the main optimisation performed. The last ECDSA-based signature verification step involves the sum of two scalar products, so introducing the Strauss-Shamir's trick to the calculation dramatically reduces gas consumption. To further optimise the function, a crafty implementation of the sum of two points is provided, using a subroutine written in assembly (i.e. a function within a function) which for the calculation of the sum of two points in Jacobian coordinates halves the calculations necessary to update the $z$ coordinate (see function *addPointAssTrick*)

Compared with [Renaud Dubois](https://github.com/rdubois-crypto/FreshCryptoLib/blob/master/solidity/src/FCL_elliptic.sol)' implementation, the proposed solution aims to be applicable to several Weierstrass Elliptic Curves defined in a finite field $F_q$. The authors were able to exploit some assumptions on the properties of the adopted curve (secp256r1) which allow saving some computations and some checks, saving further gas. To extend the applicability to any elliptic curve it is inevitable to sacrifice some gas.

The limitation of 16 state variables in the Solidity functions constitutes an impediment to the application of complex functions and calculations, such as those required for the verification of an elliptic curve-based signature. To make the procedures more efficient, it is mandatory to use the projective plane and calculate the points in affine coordinates. The proposed implementation makes use of [Jacobian coordinates](https://eprint.iacr.org/2014/1014.pdf). A further optimisation consists in adopting [Chudnovsky coordinates](https://eprint.iacr.org/2007/286.pdf), limiting the calculations for updates of the projective $z$ coordinate (as made by [Renaud Dubois](https://github.com/rdubois-crypto/FreshCryptoLib/blob/master/solidity/src/FCL_elliptic.sol)). However, generalising the applicability to different curves inevitably introduces a series of computations that make Chudnovsky's application impossible. At the current state it is not possible to introduce the [Chudnovsky coordinates](https://eprint.iacr.org/2007/286.pdf) as they would require the use of 17 state variables, leading to a compilation error. There are also other schemes for elliptic curve calculation that aim to further optimise performance. However, such schemes require numerous intermediate calculations to be kept in memory, and this is currently not possible due to some limitations of Solidity.

## Project Structure

This section explains the project structure, the main folders and describes the files content.

### On-Chain code

The project contains smart contracts to be deployed on a evm-based blockchain, and it is structured according to the best practice adopted by [nodejs](https://nodejs.org/en) and the deployment of the smart contracts was carried out via [truffle](https://archive.trufflesuite.com/docs/truffle/quickstart/).

All smart contracts are located under the ```contract/appContracts``` folder. In particular:

- *CompareECC.sol*: Contains calls to other smart contracts that implement generic operations on elliptic curves. This smart contract allows you to evaluate the gas consumed by the proposed library (*EllipticCurveMaths.sol*) compared to libraries found in literatures. In particular, the implementations of Repo1: [Witenet Foundation](https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol), Repo2: [Renaud Dubois](https://github.com/rdubois-crypto/FreshCryptoLib/blob/master/solidity/src/FCL_elliptic.sol) and Repo3: [MerklePlant](https://github.com/verklegarden/crysol/blob/main/src/onchain/secp256k1/Secp256k1Arithmetic.sol).

- *EllipticCurveMaths.sol*: Contains the proposed implementation. The library aims to be applicable to any Weierstrass elliptic curve and to save as much gas as possible for operations. All functions are implemented using assembly low level instructions, and assembly sub routines. The main method is the interleaved scalar product aimed to streamline the sum of two scalar products needed to verify a threshold signature based on ECDSA.

- *VerifyThresholdECDSA.sol*: This smart contract aims to verify an ECDSA-based digital signature that comes from an off-chain component. To do so, this smart contract has to reconstruct the message provided by the user, calculate its hash and verify the signature using the global public key. If the signature is valid, the smart contract invokes an internal transaction towards the *Source* or *Target* smart contracts, finalising an inter-chain transaction. If the signature is invalid, the smart contract invokes internal transactions towards the *Source* or *Target* smart contracts towards methods that emit specific errors regarding the incorrect signature.

- *Source* and *Target* smart contracts: These smart contracts contain the logic related to inter-chain transactions. Transactions travel from the *Source* smart contract to the *Target* smart contract. A *lock*-and-*unlock* mechanism is implemented in the *Source* smart contract for users who initiate inter-chain transactions. This prevents saturation of the target blockchain and promotes synchronisation between different blockchains. Interaction with the *Source* smart contract can occur via individual users who want to initiate an inter-chain transaction, or via off-chain processes via internal transactions via the verification smart contract. A user who initiates an inter-chain transaction invokes an internal transaction that modifies the contents of the *DataStorage* smart contract. Interactions with the *Target* smart contract can only occur via off-chain processes, tasked with producing a threshold signature that must be verified on the verification smart contract. At the moment only the use case of synchronization between two smart contracts has been provided, however, extending the use cases is very simple.

### Off-chain code

The folder off_chain_code contains the process needed to interact with the deployed smart contracts and generate threshold signatures.
The interaction to smart contracts and the off-chain processes are implemented using [Python](https://web3py.readthedocs.io/en/stable/).
In particular:

- *repositories_comparison.py*: this file contains calls to the various smart contracts tested for elliptic curve calculations: Repo1: [Witenet Foundation](https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol), Repo2: [Renaud Dubois](https://github.com/rdubois-crypto/FreshCryptoLib/blob/master/solidity/src/FCL_elliptic.sol) and Repo3: [MerklePlant](https://github.com/verklegarden/crysol/blob/main/src/onchain/secp256k1/Secp256k1Arithmetic.sol) and *EllipticCurveMaths.sol* in order to calculate their average gas consumption. For each operation of those shown in the table, 250 transactions are carried out and finally a csv is saved on which the metrics shown have been calculated.

- *elliptic_curve_operations.py*: contains the functions that implement the main operations on an elliptical curve, which are: addition of points, multiplication of points, negation of a point, and verification of belonging of a point to a certain curve. The ```Point``` and ```EllipticCurve``` objects used by the various off-chain processes are defined here.

- *shamir_secret_sharing.py*: contains functions to share a certain secret $sk$ among a set of $n$ parties. Specifically, the  following functions are implemented:
  - *lagrange_coefficient*: this function allows you to recover the Lagrange coefficient relating to a specific part $i$ in a share from a polynomial of degree $t-1$: $$\lambda_i = \prod_{\substack{1 \le j \le t \\ j \ne i}} \frac{-j}{i - j}$$
  - *generate_polynomial*: this function allows you to create a polynomial $f(x)$ of degree $t-1$, such that the coefficient $a_0$ = $f(0)$ contains the secret $sk$ to be shared with $n$ parties: $$f(x) = a_0 + a_1 x + a_2 x^2 + \cdots + a_{t-1} x^{t-1}$$
  - *share_secret*: this function implements the Shamir's Secret Sharing algorithm and allows sharing a secret $sk$ between $n$ parties. Each part obtains a pair ($i$, $f$($i$)), where $i$ is the index of the part and $f(i)$ is the value of the polynomial generated by the previous function.

- *try_simple_threshold_ecdsa.py*: this function simulates an ECDSA-based threshold digital signature. The secp256k1 elliptic curve is used in the simulation, the number of nodes $n$ is 10 and the threshold $t$ is 7. The algorithm used involves the following steps:
  1. *Key Distribution*: select a random number $sk$ (mod $p$), i.e., the secret to share. Using the procedures implemented in the *shamir_secret_sharing.py* file, the secret is divided into $n$ shares of the type ($i$, $f$($i$)), where $f$ is a polynomial of degree ($t-1$ ) randomly generated where $f(0)$ = $sk$. Each node calculates its own public key $pk_i$ = $f(i)$ $\cdot$ $G$, where $G$ is the generator point of the curve.

  After generating the shares and public keys, the procedure verifies their correctness, that is: $$sk = \sum_{i=1}^{t} \lambda_i \cdot f(i)$$ where, $\lambda_i$ is the lagrange coefficient. Then verify that the global public key is calculated correctly: $$sk \cdot G = \sum_{i=1}^{t} \lambda_i \cdot pk_i$$, where, $pk_i$ are the individual public keys of the individual parties.

  If both equalities are verified, the sharing of the secret between the various parties has occurred correctly.

  2. *Partial Signatures*: each party selects a secret nonce $k_i$ and produces its commitment on the nonce by computing the point $R_i$ = $k_i$ $\cdot$ $G$. Once the commitments have been collected, the point $$R = (x', y') = \sum_{i=1}^{t} R_i$$ is calculated, then the value $x'$ is taken as the agreed parameter for the calculation of partial signatures.

  Once the value $k$ has been agreed upon, each party produces their partial signature as follows: $$s_i ​ = (m + r \cdot f(i))⋅k^{−1}\ \text{mod}\ q$$, where $m$ is the hash of the message to be signed, $k$ is the shared nonce used by the nodes to sign the message; $r$ = $x'$ is the $x$ coordinate of the point $R$.

  3. *Threshold Signature*: Once the partial signatures $s_i$ have been calculated, they must be combined to produce the threshold signature $\sigma$. The aggregation procedure works as follows:
    $$r = r_i \Longleftrightarrow r_i = r_j \forall s_i, s_j \wedge i \neq j$$

    $$s = \sum_{i=1}^{t} \lambda_i \cdot s_i$$

    $$\sigma = (r,s)$$

  4. *Threshold Verification*: The verification is performed using the standard ECDSA verification algorithm.

- *multi_thread_threshold_ecdsa.py*: this file contains a multi-threading application simulating the off-chain nodes implementing a threshold signature based on ECDSA. Threads are divided into a primary process and a series of secondary threads. The primary process is responsible for generating the messages to be signed, sending them to the secondary threads and waiting for the partial signatures to be produced. Each secondary node produces its own signature and returns it to the primary node. The primary node, once all the signatures have been collected, is responsible for producing the threshold signature and using it to send a transaction on the blockchain. This file was used to generate metrics relating to gas consumed on various blockchains. The threshold signature scheme adopted is the one just described.

- *bc_ectss.py*: This file contains operations for constructing an ECDSA-based threshold signature that differs from the standard signature. The file contains the implementation of the *BC_ECTSS* algorithm proposed by the authors in the following [paper](https://www.sciencedirect.com/science/article/abs/pii/S2214212622001909). Specifically, here we refer to section 4 of the paper, where the authors propose a new threshold signature scheme based on ECDSA. Below is a description of the operations carried out:
  - *key_gen*: This function contains the logic for a distributed key generation protocol. We refer to section 4.2 of the [paper](https://www.sciencedirect.com/science/article/abs/pii/S2214212622001909):
    - (1) Each node $P_i$ generates a random polynomial as follows (each $a_i \in Z_q$):  $$f_i(x) = a_{i0} + a_{i1}x + a_{i2}x^2 + \cdots + a_{i(t-1)}x^{t-1}$$
    - (2) Each node $P_i$ compute its public share and broadcasts it to the other nodes:
      - (2.1) $P_i$ calculates the secret share $s_{ij} = f_i(ID_j)$ and sends it to other nodes $P_j$ in the network.
      - (2.2) $P_i$ also calculates $\eta_{i\mu} = a_{i\mu} \cdot G$ for $\mu = 0, 1, \ldots, t-1$, where $G$ is a generator of the elliptic curve group.
      - (2.3) The set {$\eta_{i0}, \eta_{i1}, \ldots, \eta_{i(t-1)}$} is broadcasted in the blockchain network.
    - (3) Each node, upon receiving the shares, verifies its correctness:
      - (3.1) $P_j$ receives the secret share $s_{ij}$ from other nodes.
      - (3.2) Node $P_j$ uses the broadcast information $\{\eta_{i0}, \eta_{i1}, \ldots, \eta_{i(t-1)}\}$ to verify the equality: $$s_{ij} \cdot G = \sum_{\mu=0}^{t-1}  \eta_{i\mu} \cdot ID_{j}^{\mu}$$
       If this equality holds, the secret share $s_{ij}$ is valid; otherwise, it is invalid.
      - (3.3) After verifying the shares, node $P_j$ calculates its own public key $PK_j$ and private key $SK_j$ as:
       $$SK_j = \sum_{u=1}^n s_{uj}, \quad PK_j = SK_j \cdot G$$
    - (4) Global public key calculation:
      - (4.1)  The signature group private key $sk$ is determined by the sum of $a_{i0}$ coefficients from all $n$ nodes: $$sk = \sum_{i=1}^n a_{i0} = F(0)$$
       where $$F(x) = \sum_{i=1}^n f_i(x)$$.
      - (4.2) Any node in the signature group can use the broadcast information to calculate the global public key $P_k$: $$P_k = \left( \sum_{i=1}^n a_{i0} \right) \cdot G \mod p$$

  - *partial_signature*: This function contains the logic for calculating the partial signature for each node. We refer to section 4.3 of the [paper](https://www.sciencedirect.com/science/article/abs/pii/S2214212622001909):
    - (1) Each node $P_i$ select a random secret $k_i \in F_q$ and compute the hash of the message $e = H(m)$;
    - (2) Each node $P_i$ calculates $r_i = x_i\ \text{mod}\ p$, where ($x_i, y_i$) = $k_i \cdot G$. If $r_i = 0$ return to (1);
    - (3) Each node $P_i$ randomly selects ($\alpha_i, \beta_i$) from $Z_q$ such that: $k_i = \alpha_i r_i + \beta_i m$, then, calculates $l_i = \alpha_i r_i + e \chi_i SK_i$, where $\chi_i$ is the lagrange coefficient (see the function *lagrange_coefficient* from the file *shamir_secret_sharing.py*) related to the node with index $i$;
    - (4) Each node $P_i$ broadcasts the partial signature $\sigma_i = (r_i, l_i, \beta_i)$ to the other nodes for the verification and the final signature aggregation.

  - *combine_partial_signatures*: This function contains the logic for generating the final threshold signature. We refer to section 4.4 of the [paper](https://www.sciencedirect.com/science/article/abs/pii/S2214212622001909):The signature combiner $P_c$ receives $t$ valid partial signatures $\sigma_i = (r_i, l_i, \beta_i)$, then $P_c$ works as follows:
    - (1) Computes $\gamma_i = (l_i + \beta_i \cdot m)$ mod $p$
    - (2) Computes the point: $$(x_i', y_i') = \gamma_i \cdot G - e \cdot \chi_i Pk_i$$ where, $G$ is the generator point of the curve, $Pk_i$ is the public key of the node $i$ and $\chi_i$ is the Lagrange coefficient of the node $i$. $P_c$ verifies if $x_i'$ = $r_i$, if it holds the signature is valid;
    - (3) Produces the threshold signature ($r$, $l$, $\beta$) as follows: $$r = \sum_{i=1}^{t} r_i;\ l = \sum_{i=1}^{t} l_i;\ \beta = \sum_{i=1}^{t} \beta_i $$

  - *verify_threshold_signature*: This function contains the logic for verifying the final threshold signature. We refer to section 4.5 of the [paper](https://www.sciencedirect.com/science/article/abs/pii/S2214212622001909): Each node in the network is equipped with the group public key $P_k$. The verification of the threshold signature involves the following steps:
    - (1) Each verifier $P_v$ computes $e = H(m)$, where $m$ is the message and $H$ is an hash function;
    - (2) Each verifier $P_v$ computes $\gamma = (l + \beta \cdot m)$ mod $p$
    - (3) Each verifier $P_v$ computes $(x',y') = \gamma \cdot G - e \cdot P_k$, then $v = x'$ mod $p$


## Deploy Configuration

To deploy and interact with smart contracts it is necessary to install the necessary node packages. The packages configuration is contained within the ```package.json``` file. To install the necessary packages it is sufficient to type from the root folder:
```
$ npm install
```
Once the packages are installed it is possible to deploy and interact with the smart contracts.

The Solidity compiler and blockchain configuration is found in the ```truffle-config.js``` file. In order to correctly compile and deploy the smart contracts it is necessary:
1. Verify the imports in the smart contract *CompareECC.sol*. If the imports from the other repositories don't work, try downloading the smart contracts and importing them locally.
2. Configure ```truffle-config.js``` appropriately. It involves the creation of the API-KEY to interact with the testnet blockchains and specify the local Besu blockchains. It can be done following the description within the file itself.

Once the setup is completed it is possible to compile the smart contracts by typing from the root folder:
```
truffle compile
```
Then, deploy the smart contracts:
```
truffle migrate --reset --network=<network-name>
```
Specifying the name of the specific network. Example, to deply on a local besu it is sufficient to type:
```
truffle migrate --reset --network=besu1
```
While for deploying on a public testnet:
```
truffle migrate --reset --network=eth_sepolia
```
Other networks are indicated in the ```networks``` section fo the ```truffle.js``` file.

***NOTICE:*** If you want to test the smart contracts on [Remix IDE](https://remix.ethereum.org/) it is mandatory to enable the optimiser under advanced settings!

## Off-Chain Settings

Python 3.10+ is required to run off-chain processes. The only additional packages needed are ```pandas``` and ```web3```, whose versions are specified in the *requirements.txt* file.

To install python you can use [Anaconda](https://docs.anaconda.com/anaconda/install/linux/) to create virtual environments or the [python](https://www.python.org/downloads/ ).

After the installation is successful, you need to install the additional packages by typing the command from the root folder:
```
pip install requirements.txt
```

***NOTICE:*** To run the code correctly, pay close attention to the connected blockchains, where the smart contacts have been deployed, and the elliptic curves used.

## Disclaimer
THIS SOFTWARE IS PROVIDED AS IS WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.
