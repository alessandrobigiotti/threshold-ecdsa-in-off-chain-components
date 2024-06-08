// SPDX-License-Identifier: Apache 2.0
pragma solidity >=0.8.0 <0.9.0;

// Auxiliary booleans to simplify the checks about the constant a
bool constant isZeroA = true;
bool constant isNegativeA = false;
bool constant isPositiveA = false;

// SECP256K1 Domain Parameters
// q is the order of the finite field Fq
uint256 constant q=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F;
// The constant a of the curve
uint256 constant a=0x0;
// The constant b of the curve
uint256 constant b=0x7;
// The x-coordinate of the generator
uint256 constant Gx=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798;
// The y-coordinate of the generator
uint256 constant Gy=0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8;
// p is the order of the abelian group Gp
uint256 constant p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141;
