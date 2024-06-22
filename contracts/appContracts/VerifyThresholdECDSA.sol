// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.8.19 <0.9.0;

import "./secp256k1.sol";
import {EllipticCurveMaths} from "./EllipticCurveMaths.sol";

interface ISourceSmartContract{
    function interChainTransactionSyncDataEnd(
        uint _nonce, address _sender, uint256 number
    ) external;

    function badSignatureNotify(
        uint _nonce, address _sender
    ) external;
}

interface ITargetSmartContract{
    function interChainTransactionSyncDataExecute(
        uint _nonce, address _from, string calldata service, uint256 number
    ) external;

    function badSignatureNotify(
        uint _nonce, address _sender
    ) external;
}

contract VerifyThresholdECDSA {

    address owner;

    address public sourceSmartContract;
    address public targetSmartContract;

    bool public checkECDSA;
    // Store the public key of the off-cahin component
    uint256 public Px = 108169464601335927917081726752577969247086109515075234060395755233675910322491;
    uint256 public Py = 22464450346750730310129665165845391043579291937531806120449729571760363935549;

    constructor(address _sourceSmartContract, address _targetSmartContract) {
        owner = msg.sender;
        sourceSmartContract = _sourceSmartContract;
        targetSmartContract = _targetSmartContract;
    }

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

    function interChainTransactionSyncDataEnd(uint _nonce, address _sender, uint256 number) external {
        require(msg.sender == address(this));
        ISourceSmartContract(sourceSmartContract).interChainTransactionSyncDataEnd(_nonce, _sender, number);
    }

    function interChainTransactionSyncDataExecute(uint _nonce, address _sender, string calldata _service, uint256 number) external {
        require(msg.sender == address(this));
        ITargetSmartContract(targetSmartContract).interChainTransactionSyncDataExecute(_nonce, _sender, _service, number);
    }

    function notifyBadSignatureEnd(uint _nonce, address _sender) external {
        require(msg.sender == address(this));
        ISourceSmartContract(sourceSmartContract).badSignatureNotify(_nonce, _sender);
    }

    function notifyBadSignatureExecute(uint _nonce, address _sender) external {
        require(msg.sender == address(this));
        ITargetSmartContract(targetSmartContract).badSignatureNotify(_nonce, _sender);
    }

    function updatePublicKeys(uint256 _Px, uint256 _Py) public returns(bool) {
        require(msg.sender == owner, "Only the owner can update the public key.");

        Px = _Px;
        Py = _Py;

        return(true);
    }

}
