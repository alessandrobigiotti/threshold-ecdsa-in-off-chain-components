// SPDX-License-Identifier: Apache 2.0
pragma solidity ^0.8.0;
/**
 * @title Performance comparison among existing repositories on elliptic curves arithmetic
 *
 * @author Alessandro Bigiotti
 */

// Be careful to select the right curve during comparison with FCL_Elliptic_ZZ and Secp256k1Arithmetic
import "./secp256k1.sol";
/* NOTICE
   Verify that the imports work, alternatively, download the smart contracts and import them from local */
/*****************************************************************************************************************************/
// Elliptic Curve from Witenet Foundation
// Repo1
import {EllipticCurve} from "https://github.com/witnet/elliptic-curve-solidity/blob/master/contracts/EllipticCurve.sol";
// ----------------------------------------------------------------------------------------------------------------------------/
// Elliptic Curve from Renaud Dubois
// Repo2
import {FCL_Elliptic_ZZ} from "https://github.com/rdubois-crypto/FreshCryptoLib/blob/master/solidity/src/FCL_elliptic.sol";
// ----------------------------------------------------------------------------------------------------------------------------/
// Elliptic Curve from Merkleplant
// Repo3
import {Secp256k1Arithmetic} from "https://github.com/pmerkleplant/crysol/blob/main/src/secp256k1/Secp256k1Arithmetic.sol";
import {ProjectivePoint, Point} from "https://github.com/pmerkleplant/crysol/blob/main/src/secp256k1/Secp256k1Arithmetic.sol";
/******************************************************************************************************************************/
// Elliptic Curve implementation proposed
// Proposed
import {EllipticCurveMaths} from "./EllipticCurveMaths.sol";


contract CompareECC{

    constructor() {

    }

    // Compare the inverse of a number under the field q
    function checkInverseBase(uint256 k) public pure returns(uint) {
        return EllipticCurve.invMod(k, q);
    }
    function checkInverseOpt(uint256 k) public view returns(uint) {
        return EllipticCurveMaths.fermatModInverse(k);
    }
    function checkInverseFCC(uint256 k) public view returns(uint) {
        return FCL_Elliptic_ZZ.FCL_pModInv(k);
    }
    function checkInverseSecp256k1(uint256 k) public view returns(uint) {
        return Secp256k1Arithmetic.modinv(k);
    }

    // Compare Jacobian Point Doubling
    function checkJacobianDoubleNormal(uint256 x, uint256 y) public pure returns(uint, uint, uint) {
        return EllipticCurve.jacDouble(x, y, 1, a, q);
    }

    function checkJacobianDoubleOpt(uint256 x, uint256 y) public pure returns(uint, uint, uint) {
        return EllipticCurveMaths.jacobianDoubling(x, y, 1);
    }
    function checkJacobianDoubleFCC(uint256 x, uint256 y) public pure returns(uint, uint, uint, uint) {
        return FCL_Elliptic_ZZ.ecZZ_Dbl(x, y, 1, 1);
    }

    // Compare Jacobian Point addition
    function checkAddPointBase(uint256 x1, uint256 y1, uint256 x2, uint256 y2) public pure returns (uint, uint, uint) {
        return  EllipticCurve.jacAdd(x1, y1, 1, x2, y2, 1, q);

    }
    function checkAddPointOpt(uint256 x1, uint256 y1, uint256 x2, uint256 y2) public pure returns (uint, uint, uint) {
        return  EllipticCurveMaths.jacobianAddition(x1, y1, 1, x2, y2, 1);
    }
    function checkAddPointFCC(uint256 x1, uint256 y1, uint256 x2, uint256 y2) public pure returns (uint, uint, uint, uint) {
        return FCL_Elliptic_ZZ.ecZZ_Add(x1, y1, 1, 1, x2, y2, 1, 1);
    }
    function checkAddPointSECP256(uint256 x1, uint256 y1, uint256 x2, uint256 y2) public pure returns(ProjectivePoint memory) {
        return Secp256k1Arithmetic.add(ProjectivePoint(x1, y1, 1), ProjectivePoint(x2, y2, 1));
    }

    // Compare Scalar Multiplication
    function checkScalarMultiplication(uint256 k, uint256 x, uint256 y) public pure returns(uint, uint) {
        return EllipticCurve.ecMul(k, x, y, a, q);
    }
    function checkScalarOptMultiplication(uint256 k, uint256 x, uint256 y) public view returns(uint, uint) {
        return EllipticCurveMaths.scalarMultiplication(k, x, y);
    }
    function checkScalrMulSecp256k1(uint256 k, uint256 x, uint256 y) public view returns(Point memory) {
        ProjectivePoint memory P = Secp256k1Arithmetic.mul(ProjectivePoint(x, y, 1), k);
        return Secp256k1Arithmetic.intoPoint(P);
    }

    // Compare the Interleaved Scalar Multiplication (Strauss-Shamir's Trick)
    function checkShamirsTrickOpt(uint256 k1, uint256 k2, uint256 Ptx, uint256 Pty) public view returns(uint) {
        return EllipticCurveMaths.interleavedScalarMultiplicationJacobian(k1, k2, Ptx, Pty);
    }

    function checkShamirTrickFCC(uint256 k1, uint256 k2, uint256 Ptx, uint256 Pty) public view returns(uint) {
        return FCL_Elliptic_ZZ.ecZZ_mulmuladd_S_asm(Ptx, Pty, k1, k2);
    }
}
