// SPDX-License-Identifier: Apache 2.0
pragma solidity >=0.8.19 <0.9.0;
/**
 * @title Maths on Elliptic Curve
 * @dev EllipticCurveMaths is a library providing arithmetic operations for
 * Weierstrass elliptic curves defined over a finite field Fq, q odd prime.
 *
 * @author Alessandro Bigiotti
 */

// import the domain parameters for the specific curve
import "./secp256k1.sol";
// import "./secp256r1.sol";
// import "./brainpoolp256r1.sol";

library EllipticCurveMaths {

    /**
    * @dev Fermat's Little Theorem to streamline the inverse of a number mod q (q is the order of the finite field)
    *
    * This function makes use of order q of the finite field Fq specified in the domain parameters of the elliptic curve imported
    * Since the order q is prime is it possible apply the Fermat's Little Theorem
    * @param num The number
    * @return q such that x*q = 1 (mod modulus)
    */
    function fermatModInverse(uint256 num) internal view returns (uint256) {
        require(num != 0 && num < q, "Invalid input");
        return expMod(num, q - 2, q);
    }


    /**
    * @dev Exponentiation using the precompiled contract at 0x05 (available after Byzantium fork)
    *
    * @param base The number
    * @param exponent The exponent
    * @param modulus The modulus
    * @return result such that base*result = 1 (mod modulus)
    */
    function expMod(uint256 base, uint256 exponent, uint256 modulus) internal view returns (uint256 result) {
        assembly ("memory-safe") {
            // Free memory pointer
            let ptr := mload(0x40)
            // Store base, exponent, modulus in memory
            mstore(ptr, 0x20)             // Length of Base (32 bytes)
            mstore(add(ptr, 0x20), 0x20)  // Length of Exponent (32 bytes)
            mstore(add(ptr, 0x40), 0x20)  // Length of Modulus (32 bytes)
            mstore(add(ptr, 0x60), base)  // Base
            mstore(add(ptr, 0x80), exponent) // Exponent
            mstore(add(ptr, 0xa0), modulus) // Modulus

            // Perform the call to the precompiled contract at 0x05
            let success := staticcall(gas(), 0x05, ptr, 0xc0, ptr, 0x20)
            if iszero(success) {
                revert(0, 0)
            }
            // Load the result
            result := mload(ptr)
        }
    }


    /**
    * @dev Extended euclidean algorithm to compute the inverse of a number mod p (p is the order of the abelian group Gp)
    *
    * This function is used for the verification of a signature based on ECDSA
    * The inverse is calculated over the order p of the abelian gourp Gp
    * There is no guarantee that p is prime like q, so is not possible apply the Fermat's Little Theorem
    *
    * @param num The number
    * @return quotient such that num*quotient = 1 (mod p)
    */
    function invMod(uint256 num) public pure returns(uint256 quotient) {

        assembly ("memory-safe") {
            // Check the initial conditions: num > 0 and num < p
            if or(iszero(num), eq(num, p)) {
                revert(0, 0)
            }

            // Initialize variables
            quotient := 0
            let newT := 1
            let r := p
            let t := 0

            // Loop until the num becomes 0
            for { } gt(num, 0) { } {
                // Calculate t = r / x
                t := div(r, num)

                // Calculate newT and update the quotient
                // newT = (quotient + (p - (t * newT) % p)) % p
                // quotient = newT (from previous iteration)
                let tempMul := mulmod(t, newT, p)
                let tempSub := sub(p, tempMul)
                let tempNewT := addmod(quotient, tempSub, p)

                quotient := newT
                newT := tempNewT

                // Update r and num for the next iteration
                let tempNum := sub(r, mul(t, num))
                r := num
                num := tempNum
            }
        }
    }



    /**
    * @dev Function to check if a given point (x, y) lies on the elliptic curve y^2 = x^3 + ax + b over a finite field Fq
    * The point (x,y) must be within the Group Gp
    *
    * @param x The ccordinate x of the point
    * @param y The coordinate y of the point
    * @return true or false depending on the condition (x,y) in Gp
    */
    function isPointOnCurve(uint x, uint y)
        internal pure returns (bool)
    {
        // Check the curve constraints
        require(q > 3, "q must be greater than 3");
        require(x < q && y < q, "x and y must be less than q");

        uint y2;
        uint rhs;
        assembly ("memory-safe") {
            // Compute y^2
            y2 := mulmod(y, y, q)
            // Compute x^3
            let x3 := mulmod(x, mulmod(x, x, q), q)
            // Compute a*x
            let ax := mulmod(a, x, q)
            // Compute rhs = x^3 + ax + b
            rhs := addmod(addmod(x3, ax, q), b, q)
        }

        // Check if the point satisfies the curve equation
        return y2 == rhs;
    }

    /**
    * @dev Function to calculate the poitn addition in Jacobian coordinates
    *
    * @param x1 The x-coodinate x of the first point
    * @param y1 The y-coodinate y of the first point
    * @param z1 The z-coodinate z of the first point
    * @param x2 The x-coodinate x of the second point
    * @param y2 The y-coodinate y of the second point
    * @param z2 The z.coodinate z of the second point
    * @return xf The final Jacobian x-coordinate
    * @return yf The final Jacobian y-coordinate
    * @return zf The final Jacobian z-coordinate
    */
    function jacobianAddition(uint256 x1, uint256 y1, uint256 z1, uint256 x2, uint256 y2, uint256 z2)
        internal pure returns (uint256 xf, uint256 yf, uint256 zf)
    {
        // If the first point is 0 return the second point
        if (x1 == 0 && y1 == 0) return (x2, y2, z2);
        // If the second point is 0 return the first point
        if (x2 == 0 && y2 == 0) return (x1, y1, z1);

        assembly ("memory-safe") {
            // Store z1^2, z1^3, z2^2, z2^3
            let u1 := mulmod(z2, z2, q)
            let s1 := mulmod(z2, u1, q)
            let u2 := mulmod(z1, z1, q)
            let s2 := mulmod(z1, u2, q)
            // Compute the values u1, u2, s1, s2
            // u1 = x1 * z2^2
            u1 := mulmod(x1, u1, q)
            // u2 = x2 * z2^3
            u2 := mulmod(x2, u2, q)
            // s1 = y1 * z1^2
            s1 := mulmod(y1, s1, q)
            // s2 = y2 * z1^3
            s2 := mulmod(y2, s2, q)

            // Check that u1 != u2
            if iszero(eq(u2, u1)) {
                // Compute h = u2 - u1
                let h := addmod(u2, sub(q, u1), q)
                // Compute r = s2 - s1
                let r := addmod(s2, sub(q, s1), q)
                // Store h^2 and h^3
                let h2 := mulmod(h, h, q)
                let h3 := mulmod(h2, h, q)

                // xf = r^2 -h^3 -2*u1*h^2
                xf := mulmod(u1, h2, q)
                xf := mulmod(2, xf, q)
                xf := addmod(addmod(mulmod(r, r, q), sub(q, h3), q), sub(q, xf), q)

                // yf = r*(u1*h^2 - x^3) - s1*z1*h^3
                yf := mulmod(u1, h2, q)
                yf := mulmod(r,addmod(yf, sub(q, xf), q), q)
                yf := addmod(yf, sub(q, mulmod(s1, h3, q)), q)

                // zf = h * z1 * z2
                zf := mulmod(h, mulmod(z1, z2, q), q)

            }

            // Check if u1 == u2
            if eq(u2, u1) {
                // Check if s1 == s2
                if eq(s2, s1) {
                    // The point are equal, perform the double algorithm
                    // Inline Jacobian double
                    // Store x^2
                    xf := mulmod(x1, x1, q)
                    // Store y^2
                    yf := mulmod(y1, y1, q)

                    // Compute s := 4 * x * y^2
                    let s := mulmod(4, mulmod(x1, yf, q), q)
                    // Compute m := 3*x^2 + a*z^4
                    let m
                    // Save gas if a = 0
                    if eq(isZeroA, 1) {
                        m := mulmod(3, xf, q)
                    }
                    if eq(isZeroA, 0) {
                        zf := mulmod(z1, z1, q)
                        m := addmod(mulmod(3, xf, q), mulmod(a, mulmod(zf, zf, q), q), q)
                    }
                    // xf := m^2 - 2s
                    xf := addmod(mulmod(m, m, q), sub(q, addmod(s, s, q)), q)
                    // yf := m(s-xf) - 8*y1^4
                    yf := addmod(mulmod(m, addmod(s, sub(q, xf), q), q), sub(q, mulmod(8, mulmod(yf, yf, q), q)), q)
                    // zf := 2*y*z
                    zf := mulmod(2, mulmod(y1, z1, q), q)

                }
                // If s1 != s2 return the point at infinity depending on the value of a
                if iszero(eq(s2, s1)) {
                    if eq(isZeroA, 1) {
                        xf := 0
                        yf := 0
                        zf := 1
                    }
                    if eq(isNegativeA, 1) {
                        xf := 1
                        yf := 0
                        zf := 1
                    }
                    if eq(isPositiveA, 1) {
                        xf := 1
                        yf := 1
                        zf := 0
                    }
                }
            }
        }
        return (xf, yf, zf);
    }


    /**
    * @dev Function to calculate the point doubling in Jacobian coordinates
    *
    * @param x The x-coordinate of the point in Jacobian coordinates
    * @param y The y-coordinate of the point in Jacobian coordinates
    * @param z The z-coordinate of the point in Jacobian coordinates
    * @return xf The final x-coordinate after doubling
    * @return yf The final y-coordinate after doubling
    * @return zf The final z-coordinate after doubling
    */
    function jacobianDoubling(uint256 x, uint256 y, uint256 z)
        internal pure
        returns (uint256 xf, uint256 yf, uint256 zf)
    {
        // If z = 0 return the current point
        if (z == 0) return (x, y, z);

        assembly ("memory-safe") {
            // Store x^2
            xf := mulmod(x, x, q)
            // Store y^2
            yf := mulmod(y, y, q)

            // Compute s := 4 * x * y^2
            let s := mulmod(4, mulmod(x, yf, q), q)
            // Compute m := 3* x^2 + a * z^4
            let m
            // Save gas if a = 0
            if eq(isZeroA, 1) {
                m := mulmod(3, xf, q)
            }
            if eq(isZeroA, 0) {
                zf := mulmod(z, z, q)
                m := addmod(mulmod(3, xf, q), mulmod(a, mulmod(zf, zf, q), q), q)
            }
            // xf := m^2 - 2s
            xf := addmod(mulmod(m, m, q), sub(q, addmod(s, s, q)), q)
            // yf := m(s-xf) - 8*y1^4
            yf := addmod(mulmod(m, addmod(s, sub(q, xf), q), q), sub(q, mulmod(8, mulmod(yf, yf, q), q)), q)
            // zf := 2*y*z
            zf := mulmod(2, mulmod(y, z, q), q)

        }

        return(xf, yf, zf);

    }



    /**
    * @dev Multiply a point (x, y) for a scalar k using the double and add algorithm in Jacobian coordinates
    *
    * @param k The scalar to multiply
    * @param x The x-coordinate of the point
    * @param y The y-coordinate of the point
    * @return xf The final x-coordinate
    * @return yf The final y-coordinate
    */
    function scalarMultiplication(uint256 k, uint256 x, uint256 y)
        internal view
        returns (uint256 xf, uint256 yf)
    {
        // Jacobian multiplication
        (xf, yf) = jacobianMultiplication(k, x, y, 1);
        return (xf, yf);
    }

    /**
    * @dev Function to compute the scalar product between a scalar k and a Jacobian point (x, y, z)
    *
    * @param k The scalar to multiply
    * @param x The x-coordinate of the point
    * @param y The y-coordinate of the point
    * @param z The z-coordinate of the point
    * @return xf The final x-coordinate
    * @return yf The final y-coordinate
    */
    function jacobianMultiplication(uint256 k, uint256 x, uint256 y, uint256 z)
        internal view
        returns (uint256 xf, uint256 yf)
    {
        // Early return in case that k == 0
        if (k == 0) {
            return (x, y);
        }

        // Start with the point at infinity in Jacobian coordinates
        uint256 zf;

        // Verify if the constant a of the curve is 0, <0 or >0 and set the point at infinity in Jacobian coordinates
        assembly ("memory-safe") {
            if eq(isZeroA, 1) {
                xf := 0
                yf := 0
                zf := 1
            }
            if eq(isNegativeA, 1) {
                xf := 1
                yf := 0
                zf := 1
            }
            if eq(isPositiveA, 1) {
                xf := 0
                yf := 0
                zf := 0
            }
        }

        // Double and add algorithm
        while (k != 0) {
            if ((k & 1) != 0) {
                // If the current bit == 1 add the current point to the original point
                (xf, yf, zf) = jacobianAddition(xf, yf, zf, x, y, z);
            }
            k = k >> 1;
            // Always double the point
            (x, y, z) = jacobianDoubling(x, y, z);
        }
        return toAffine(xf, yf, zf);
    }

    /**
    * @dev Function to perform Straus's Shamir's Trick (k1 * G + k2 * Pk)
    * This function is used only to speed up the verification of the ECDSA signature
    *
    * @param k1 The scalar to multiply per the generator point G
    * @param k2 The scalar to multiply per the public key Pk
    * @param pkx The x-coordinate of the public key
    * @param pky The y-coordinate of the public key
    * @return rx The x-coordinate of the result mod p
    */
    function interleavedScalarMultiplicationJacobian(uint256 k1, uint256 k2, uint256 pkx, uint256 pky
    ) internal view returns (uint256 rx) {
        // k1 and k2 cannot be = 0 since are the parameters u1 and u2 for the sign verification
        // We can avoid this check

        uint256 ry;
        uint256 rz;

        // Precompute the values Pk + G in precX and precY
        uint256 precX;
        uint256 precY;
        uint256 precZ;
        (precX, precY, precZ) = jacobianAddition(pkx, pky, 1, Gx, Gy, 1);
        (precX, precY) = toAffine(precX, precY, precZ);

        // Start the Strauss-Shamir's Trick
        assembly ("memory-safe") {

            // Idetnify the max scalar and get its bit length
            let lengthx := k1
            if gt(k2, k1) {
                lengthx := k2
            }
            lengthx := findNumBits(lengthx)

            // Set the point at infinity depending on the type of the curve
            if eq(isZeroA, 1) {
                rx := 0
                ry := 0
                rz := 1
            }
            if eq(isNegativeA, 1) {
                rx := 1
                ry := 0
                rz := 1
            }
            if eq(isPositiveA, 1) {
                rx := 0
                ry := 0
                rz := 0
            }

            // Apply the Strauss-Shamir's Trick rules
            for {let i := lengthx} gt(i, 0) {i := sub(i, 1)} {
                // Compute the i-th bit of k1 and k2
                let bitK1 := and(shr(sub(i, 1), k1), 1)
                let bitK2 := and(shr(sub(i, 1), k2), 1)

                // if z != 0 double the current point
                if iszero(eq(rz, 0)) {
                    rx, ry, rz := doublePointAss(rx, ry, rz)
                }
                // if the i-th bit of k1 = 1 add G to the current point
                if and(eq(bitK1, 1), eq(bitK2, 0))  {
                    rx, ry, rz := addPointAssTrick(rx, ry, rz, Gx, Gy, 1)
                    continue
                }
                // if the i-th bit of k2 = 1 add Pk to the current point
                if and(eq(bitK1, 0), eq(bitK2, 1)) {
                    rx, ry, rz := addPointAssTrick(rx, ry, rz, pkx, pky, 1)
                    continue
                }
                // if both the i-th bits of k1 and k2 are 1 add Pk + G to the current point
                if and(eq(bitK1, 1), eq(bitK2, 1)){
                    rx, ry, rz := addPointAssTrick(rx, ry, rz, precX, precY, 1)
                    continue
                }

            }
            /****************************************************************/
            /* AUXILIARY FUNCTIONS                                          */
            /****************************************************************/
            // Find the number of bits of the max scalar
            // The function uses the binary search to find the number of bits
            function findNumBits(length) -> count {
                count := 0
                if gt(length, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF) {
                    length := shr(128, length)
                    count := add(count, 128)
                }
                if gt(length, 0xFFFFFFFFFFFFFFFF) {
                    length := shr(64, length)
                    count := add(count, 64)
                }
                if gt(length, 0xFFFFFFFF) {
                    length := shr(32, length)
                    count := add(count, 32)
                }
                if gt(length, 0xFFFF) {
                    length := shr(16, length)
                    count := add(count, 16)
                }
                if gt(length, 0xFF) {
                    length := shr(8, length)
                    count := add(count, 8)
                }
                if gt(length, 0xF) {
                    length := shr(4, length)
                    count := add(count, 4)
                }
                if gt(length, 0x3) {
                    length := shr(2, length)
                    count := add(count, 2)
                }
                if gt(length, 0x1) {
                    length := shr(1, length)
                    count := add(count, 1)
                }
                count := add(count, length)
            }

            // Calculate double point
            function doublePointAss(x, y, z) -> xf, yf, zf {
                // Store x^2
                xf := mulmod(x, x, q)
                // Store y^2
                yf := mulmod(y, y, q)

                // s := 4 * x * y^2
                let s := mulmod(4, mulmod(x, yf, q), q)
                // m := 3* x^2 + a * z^4
                let m
                // Check a to save gas
                if eq(isZeroA, 1) {
                    m := mulmod(3, xf, q)
                    // xf := m^2 - 2s
                    xf := addmod(mulmod(m, m, q), sub(q, addmod(s, s, q)), q)
                    // yf := m(s-xf) -8*y1^4
                    yf := addmod(mulmod(m, addmod(s, sub(q, xf), q), q), sub(q, mulmod(8, mulmod(yf, yf, q), q)), q)
                    // zf := 2*y*z
                    zf := mulmod(2, mulmod(y, z, q), q)
                    leave // exit the function
                }
                if eq(isZeroA, 0) {
                    // Check z to save gas
                    if iszero(eq(z, 1)) {
                        zf := mulmod(z, z, q)
                        m := addmod(mulmod(3, xf, q), mulmod(a, mulmod(zf, zf, q), q), q)
                        // xf := m^2 - 2s
                        xf := addmod(mulmod(m, m, q), sub(q, addmod(s, s, q)), q)
                        // yf := m(s-xf) - 8*y1^4
                        yf := addmod(mulmod(m, addmod(s, sub(q, xf), q), q), sub(q, mulmod(8, mulmod(yf, yf, q), q)), q)
                        // zf := 2*y*z
                        zf := mulmod(2, mulmod(y, z, q), q)
                        leave // exit the function
                    }
                    // If z == 1
                    m := addmod(mulmod(3, xf, q), a, q)
                    // xf := m^2 - 2s
                    xf := addmod(mulmod(m, m, q), sub(q, addmod(s, s, q)), q)
                    // yf := m(s-xf) - 8*y1^4
                    yf := addmod(mulmod(m, addmod(s, sub(q, xf), q), q), sub(q, mulmod(8, mulmod(yf, yf, q), q)), q)
                    // zf := 2*y*z
                    zf := mulmod(2, mulmod(y, z, q), q)

                }
            }

            // Calculate the point addition only in case P2 has z2 = 1
            function addPointAssTrick(x1, y1, z1, x2, y2, z2) -> xf, yf, zf {
                // If the first point is zero return the second point
                // The second point cannot be 0 as it can be G, Pk or Pk + G
                if and(and(eq(x1, 0), eq(y1, 0)), eq(z1, 0)) {
                    xf := x2
                    yf := y2
                    zf := z2
                    leave
                }

                // Compute u1, u2, s1, s2
                let u2 := mulmod(z1, z1, q)
                let s2 := mulmod(z1, u2, q)

                let u1 := x1
                u2 := mulmod(x2, u2, q)
                let s1 := y1
                s2 := mulmod(y2, s2, q)

                // If u1 != u2 apply the Jacobian addition
                if iszero(eq(u2, u1)) {

                    let h := addmod(u2, sub(q, u1), q)
                    let r := addmod(s2, sub(q, s1), q)
                    let h2 := mulmod(h, h, q)
                    let h3 := mulmod(h2, h, q)

                    xf := mulmod(u1, h2, q)
                    xf := mulmod(2, xf, q)
                    xf := addmod(addmod(mulmod(r, r, q), sub(q, h3), q), sub(q, xf), q)

                    yf := mulmod(u1, h2, q)
                    yf := mulmod(r,addmod(yf, sub(q, xf), q), q)
                    yf := addmod(yf, sub(q, mulmod(s1, h3, q)), q)

                    zf := mulmod(h, mulmod(z1, z2, q), q)
                    leave
                }
                // If u1 = u2
                if eq(u2, u1) {
                    // If s1 = s1
                    if eq(s2, s1) {
                        // Double the current point
                        xf, yf, zf := doublePointAss(x1, y1, z1)
                        leave

                    }
                    // If S1 != s2 return the point at infinity depending on the value of a
                    if iszero(eq(s2, s1)) {
                        if eq(isZeroA, 1) {
                            xf := 0
                            yf := 0
                            zf := 1
                            leave
                        }
                        if eq(isNegativeA, 1) {
                            xf := 1
                            yf := 0
                            zf := 1
                            leave
                        }
                        if eq(isPositiveA, 1) {
                            xf := 0
                            yf := 0
                            zf := 0
                            leave
                        }
                    }
                }
            }
        }
        return toAffineECDSA(rx, rz);
    }

    /**
    * @dev Converts a point (x, y, z) expressed in Jacobian coordinates to affine coordinates (xf, yf, 1)
    *
    * @param x The Jacobian x-coordinate
    * @param y The Jacobian y-coordinate
    * @param z The Jacobian z-coordinate
    * @return xf The x-coordinate
    * @return yf The y-coordinate
    */
    function toAffine(uint256 x, uint256 y, uint256 z)
        internal view
        returns (uint256 xf, uint256 yf)
    {
        // Store z^-1
        uint256 zInv = fermatModInverse(z);
        assembly ("memory-safe") {
            // Store (z^-1)^2
            let zInv2 := mulmod(zInv, zInv, q)
            // Compute xf = x * (z^-1)^2
            xf := mulmod(x, zInv2, q)
            // Compute yf = y * (z^-1)^3
            yf := mulmod(y, mulmod(zInv, zInv2, q), q)
        }

        return (xf, yf);
    }


    /**
    * @dev Function to convert a point in affine coordinates only for the verification of the ECDSA
    *
    * @param x The Jacobian x-coordinate
    * @param z The Jacobian z-coordinate
    * @return xf The affine coordinate x (mod p)
    */
    function toAffineECDSA(uint x, uint z)
        internal view
        returns (uint xf)
    {
        // Store z^-1
        uint256 zInv = fermatModInverse(z);
        assembly ("memory-safe") {
            // Store (z^-1)^2
            let zInv2 := mulmod(zInv, zInv, q)
            // Compute xf = x * (z^-1)^2 (mod p)
            xf := mod(mulmod(x, zInv2, q), p)
        }

        return xf;
    }


      /**
      * @dev This function calculates the double of a point on an elliptic curve.
      *
      * @param x The x-coordinate of the point
      * @param y The y-coordinate of the point
      * @return xf The final x-coordinate
      * @return yf The final y-coordinate
      */
      function doublePoint(uint256 x, uint256 y) internal view returns (uint xf, uint yf) {
          // lambda = x^2 (save x^2 to avoid repiting the calculation)
          uint256 lambda = expMod(x, 2, q);
          assembly ("memory-safe") {
              // lambda = 3 * x^2 + a
              lambda := addmod(mulmod(3, lambda, q), a, q)
          }
          // lambda = (3 * x^2 + a) * (2y)^-1
          lambda = mulmod(lambda, fermatModInverse(mulmod(2, y, q)), q);

          // store in xf the value lambda^2
          xf = expMod(lambda, 2, q);

          assembly ("memory-safe") {
              // Compute the final coordinates
              // xf := lambda^2 -2x
              xf := addmod(addmod(xf, sub(q, x), q), sub(q, x), q)
              // yf := lambda*(x - xf)-y
              yf := addmod(mulmod(lambda, addmod(x, sub(q, xf), q), q), sub(q, y), q)
          }

          return (xf, yf);
      }


      /**
      * @dev Elliptic curve point addition
      *
      * @param x1 The x-coordinate of the first point
      * @param y1 The y-coordinate of the first point
      * @param x2 The x-coordinate of the second point
      * @param y2 The y-coordinate of the second point
      * @return xf The final x-coordinate
      * @return yf The final y-coordinate
      */
      function addPoint(uint256 x1, uint256 y1, uint256 x2, uint256 y2) internal view returns (uint xf, uint yf) {
          // If the points are equal perform the point addition
          if (x1 == x2 && y1 == y2) {
              // Point doubling
              return doublePoint(x1, y1);

          } else {
              // Point addition
              // Store lambda = (y2 - y1) / (x2 - x1)
              uint256 lambda = mulmod(addmod(y2,  q - y1,  q), fermatModInverse(addmod(x2,  q - x1,  q)),  q);

              // calculate lambda^2
              xf = expMod(lambda, 2,  q);
              assembly ("memory-safe") {
                  // calculate xf = lambda^2 - x1 - x2
                  xf := addmod(addmod(xf,  sub(q, x1),  q),  sub(q, x2),  q)
              }

              assembly ("memory-safe") {
                  // calculate yf = lambda(x1 - xf) - y1
                  yf := addmod(mulmod(lambda, addmod(x1,  sub(q, xf),  q),  q),  sub(q, y1),  q)
              }

              return (xf, yf);
          }
      }

}
