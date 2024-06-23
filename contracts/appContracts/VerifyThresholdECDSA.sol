// SPDX-License-Identifier: Apache 2.0
pragma solidity >=0.8.19 <0.9.0;
/**
 * @title Verify Threshold ECDSA in Inter-Chain Transactions
 * @dev VerifyThresholdECDSA is a smart contract that contains functions for
 * verifying an ecdsa-based threshold signature to regulate user activities
 * and finalise interchain transactions.
 *
 * @author Alessandro Bigiotti
 */

// import the domain parameters for the specific curve
import "./secp256k1.sol";
// import "./secp256r1.sol";
// import "./brainpoolp256r1.sol";

// import the library to compute the elliptic curve operations
import {EllipticCurveMaths} from "./EllipticCurveMaths.sol";

// Interface for internal transactions towards the SourceSmartContract
interface ISourceSmartContract{
    function interChainTransactionSyncDataEnd(
        uint _nonce, address _sender, uint256 number
    ) external;

    function badSignatureNotify(
        uint _nonce, address _sender
    ) external;
}

// Interface for internal transactions towards the TargetSmartContract
interface ITargetSmartContract{
    function interChainTransactionSyncDataExecute(
        uint _nonce, address _from, string calldata service, uint256 number
    ) external;

    function badSignatureNotify(
        uint _nonce, address _sender
    ) external;
}


contract VerifyThresholdECDSA {

    // The address of the person who deployed the smart contract
    address owner;

    // The addresses of the source and target smart contracts
    address public sourceSmartContract;
    address public targetSmartContract;

    // A variable needed to compute the gas consumption of the method: verifyECDSA
    bool public checkECDSA;
    // Store the public key of the off-cahin component
    uint256 public Px = 108169464601335927917081726752577969247086109515075234060395755233675910322491;
    uint256 public Py = 22464450346750730310129665165845391043579291937531806120449729571760363935549;

    // At the time of deployment, the addresses of the source and
    // destination smart contracts must be specified
    constructor(address _sourceSmartContract, address _targetSmartContract) {
        owner = msg.sender;
        sourceSmartContract = _sourceSmartContract;
        targetSmartContract = _targetSmartContract;
    }

    /**
     * @dev This function is used for verifying ECDSA digital signatures.
     *
     * The signature verification process involves several steps:
     * - Checking if the provided r and s values are within valid range (r > 0 && r < p, s > 0 && s < p).
     * - Compute s^-1 mod p, where s^-1 is the modular multiplicative inverse of s.
     * - Compute u1 = H(m) * s^-1 and u2 = r * s^-1, where m is the message to be signed,
     *   H() is a hash function (in this case keccak256), and p is the order of the elliptic curve.
     * - Compute fx = ecmul(u1, u2) using interleaved scalar multiplication on Jacobian coordinates.
     * - The signature is valid if and only if fx == r holds true.
     *
     * @param hashInt Hash of the message to be signed.
     * @param r First coordinate of the public key used for signing.
     * @param s Second coordinate of the public key used for signing.
     *
     * @return Returns true if the signature is valid, false otherwise.
     */
    function verifySignature(uint256 hashInt, uint256 r, uint256 s) public view returns(bool) {
        require(r > 0 && r < p);
        require(s > 0 && s < p);
        // Compute s^-1 mod p
        uint sinv = EllipticCurveMaths.invMod(s);
        // Compute the value u1 = H(m) * s^-1
        uint u1 = mulmod(sinv, hashInt, p);
        // Compute the value u2 = r * s^-1
        uint u2 = mulmod(r, sinv, p);
        uint fx = EllipticCurveMaths.interleavedScalarMultiplicationJacobian(u1, u2, Px, Py);
        require(fx == r);
        return (fx == r);
    }

    /**
     * @dev This function verifies an ECDSA digital signature.
     *
     * The function works by checking if provided r and s values are within valid range (r > 0 && r < p, s > 0 && s < p).
     * It then computes u1 = H(m) * s^-1 and u2 = r * s^-1 where m is the message to be signed.
     * The function then uses interleaved scalar multiplication on Jacobian coordinates to compute fx = ecmul(u1, u2).
     * The signature is valid if and only if fx == r holds true.
     *
     * This function is used only for testing purposes
     *
     * @param _nonce Nonce of the transaction.
     * @param _sender Address of the sender.
     * @param val Value associated with the transaction.
     * @param r First coordinate of the public key used for signing.
     * @param s Second coordinate of the public key used for signing.
     *
     * @return Returns true if the signature is valid, false otherwise.
     */
    function verifyECDSA(uint256 _nonce, uint256 val1, uint256 val2, string calldata val3, uint256 r, uint256 s) public returns(bool) {
       require(r > 0 && r < p, "The r value must be greater than 0 and less than p");
       require(s > 0 && s < p, "The s value must be greater than 0 and less than p");
       // Hash the message
       bytes32 messageHash = keccak256(abi.encodePacked(val1, val2, val3, msg.sender, _nonce));

       if (verifySignature(uint(messageHash), r, s)) {
           // Start an inter-chain transaction...
           checkECDSA = true;
           return true;
       }
       checkECDSA = false;
       return false;
    }

    /**
     * Brief: Verifies an ECDSA digital signature specifically designed for inter-chain synchronisation data end.
     *        This function is linked to the source smart contract and has the task of finalising the inter-chain
     *        transaction and rehabilitating the user who started an inter-chain transaction.
     *
     * The function works by checking if provided r and s values are within valid range (r > 0 && r < p, s > 0 && s < p).
     * In the case r = 0 and s = 0 means the signature is not valid. An internal transaction invokes the badSignatureNotify
     * of the source smart contract.
     *
     * If the signature is valid, this function complete an inter-chain transaction by enabling the user with address
     * sender to send inter-chain transaction again
     *
     * @param _nonce Virtual Nonce of the transaction.
     * @param _sender Address of the sender.
     * @param val Value associated with the transaction.
     * @param r First coordinate of the public key used for signing.
     * @param s Second coordinate of the public key used for signing.
     *
     * @return Returns true if the signature is valid, false otherwise.
     */
    function verifyECDSAForInterChainSyncDataEnd(
      uint256 _nonce, address _sender, uint256 val, uint256 r, uint256 s
    ) public returns(bool) {
        if (r == 0 && s == 0) {
            this.notifyBadSignatureEnd(_nonce, _sender);
            return false;
        }

        bytes32 messageHash = keccak256(abi.encodePacked(_nonce, _sender, val));
        if (verifySignature(uint(messageHash), r, s)) {
            this.interChainTransactionSyncDataEnd(_nonce, _sender, val);
            return true;
        }

        return false;
    }

    /**
     * Brief: Verifies an ECDSA digital signature specifically designed for inter-chain execution.
     *        This function is linked to the target smart contract and has the task of executing an inter-chain
     *        transaction on the target smart contract.
     *
     * The function works by checking if provided r and s values are within valid range (r > 0 && r < p, s > 0 && s < p).
     * In the case r = 0 and s = 0 means the signature is not valid. An internal transaction invokes the badSignatureNotify
     * of the target smart contract.
     *
     * @param _nonce Nonce of the transaction.
     * @param _sender Address of the sender.
     * @param val Value associated with the transaction.
     * @param r First coordinate of the public key used for signing.
     * @param s Second coordinate of the public key used for signing.
     *
     * @return Returns true if the signature is valid, false otherwise.
     */
    function verifyECDSAForInterChainSyncDataExecution(
        uint256 _nonce, address _sender, uint256 val, uint256 r, uint256 s
    ) public returns(bool) {
        if (r == 0 && s == 0) {
            this.notifyBadSignatureExecute(_nonce, _sender);
            return false;
        }

        bytes32 messageHash = keccak256(abi.encodePacked(_nonce, _sender, val));

        if (verifySignature(uint(messageHash), r, s)) {
            this.interChainTransactionSyncDataExecute(_nonce, _sender, "SYNC_DATA", val);
            return true;
        }

        return false;

    }

    /**
     * @dev This function is used to end an inter-chain transaction aimed at synchronising smart contracts data.
     * The function first verifies if the caller is the contract itself, then it calls the corresponding
     * function in the source smart contract with provided nonce, sender and value. The transaction unlocks the user
     * who initiated an inter-chain transaction.
     *
     * @param _nonce Nonce of the transaction.
     * @param _sender Address of the sender.
     * @param number Value associated with the transaction.
     */
    function interChainTransactionSyncDataEnd(uint _nonce, address _sender, uint256 number) external {
        require(msg.sender == address(this), "The function can be invoked only by this smart contract.");
        ISourceSmartContract(sourceSmartContract).interChainTransactionSyncDataEnd(_nonce, _sender, number);
    }

    /**
     * @dev This function is used to execute an inter-chain transaction aimed at synchronising smart contracts data.
     * The function first verifies if the caller is the contract itself, then it calls the corresponding
     * function in the target smart contract with provided nonce, sender and value.
     *
     * @param _nonce Nonce of the transaction.
     * @param _sender Address of the sender.
     * @param number Value associated with the transaction.
     */
    function interChainTransactionSyncDataExecute(uint _nonce, address _sender, string calldata _service, uint256 number) external {
        require(msg.sender == address(this), "The function can be invoked only by this smart contract.");
        ITargetSmartContract(targetSmartContract).interChainTransactionSyncDataExecute(_nonce, _sender, _service, number);
    }

    /**
     * @dev This function notifies about bad ECDSA digital signature for inter-chain synchronization data end.
     *
     * The function checks if the sender is the contract itself, and then calls the `badSignatureNotify`
     * function of the source smart contract with provided nonce and sender address.
     * This function should be called when a bad ECDSA signature is detected for inter-chain synchronization data end.
     *
     * @param _nonce Nonce of the transaction.
     * @param _sender Address of the sender.
     */
    function notifyBadSignatureEnd(uint _nonce, address _sender) external {
        require(msg.sender == address(this), "The function can be invoked only by this smart contract.");
        ISourceSmartContract(sourceSmartContract).badSignatureNotify(_nonce, _sender);
    }

    /**
     * @dev This function notifies about bad ECDSA digital signature for executing an inter-chain transaction.
     *
     * The function checks if the sender is the contract itself, and then calls the `badSignatureNotify`
     * function of the target smart contract with provided nonce and sender address.
     * This function should be called when a bad ECDSA signature is detected for the execution of an inter-chain transaction.
     *
     * @param _nonce Nonce of the transaction.
     * @param _sender Address of the sender.
     */
    function notifyBadSignatureExecute(uint _nonce, address _sender) external {
        require(msg.sender == address(this), "The function can be invoked only by this smart contract.");
        ITargetSmartContract(targetSmartContract).badSignatureNotify(_nonce, _sender);
    }

    function updatePublicKey(uint256 _Px, uint256 _Py) public returns(bool) {
        require(msg.sender == owner, "Only the owner can update the public key.");

        Px = _Px;
        Py = _Py;

        return(true);
    }

}
