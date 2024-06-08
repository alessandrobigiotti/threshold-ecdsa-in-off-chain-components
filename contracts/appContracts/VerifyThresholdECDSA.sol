// SPDX-License-Identifier: Apache 2.0
pragma solidity >=0.8.0 <0.9.0;
/**
 * @title Verify Threshold ECDSA
 * @dev This Smart Contract makes use of EllipticCurveMaths.sol to verify an ECDSA
 * signature coming from an off-chain component
 *
 * @author Alessandro Bigiotti
 */
import "./secp256k1.sol";
import {EllipticCurveMaths} from "./EllipticCurveMaths.sol";
contract VerifyThresholdECDSA {

    address owner;
    mapping(address => uint256) public nonceMap;

    // Store the public key of the off-cahin component
    uint256 public Px = 108169464601335927917081726752577969247086109515075234060395755233675910322491;
    uint256 public Py = 22464450346750730310129665165845391043579291937531806120449729571760363935549;

    constructor() {
        nonceMap[msg.sender] = 0;
    }

    function verifySignature(uint256 hashInt, uint256 r, uint256 s) public view returns(bool) {
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
        require(nonceMap[msg.sender]+1 == _nonce, "Invalid nonce");
        require(r > 0 && r < p, "The r value must be greater than 0 and less than p");
        require(s > 0 && s < p, "The s value must be greater than 0 and less than p");
        // Hash the message
        bytes32 messageHash = keccak256(abi.encodePacked(val1, val2, val3, msg.sender, _nonce));

        if (verifySignature(uint(messageHash), r, s)) {
            nonceMap[msg.sender] = _nonce;
            // Start an inter-chain transaction...
            return true;
        }

        return false;
    }

    function updatePublicKey(uint256 _Px, uint256 _Py) public returns(bool) {
        require(msg.sender == owner, "Only the owner can update the public key.");

        Px = _Px;
        Py = _Py;

        return(true);
    }

    function getNonce() public view returns(uint256) {
        return nonceMap[msg.sender];
    }
}
