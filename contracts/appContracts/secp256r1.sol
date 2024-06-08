// SPDX-License-Identifier: Apache 2.0
pragma solidity >=0.8.0 <0.9.0;

// Auxiliary booleans to simplify the checks about the constant a
bool constant isZeroA = false;
bool constant isNegativeA = true;
bool constant isPositiveA = false;

// SECP256R1 Domain Parameters
// q is the order of the finite field Fq
uint256 constant q = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF;
// The constant a of the curve
uint256 constant a = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC;
// The constant b of the curve
uint256 constant b = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B;
// The x-coordinate of the generator
uint256 constant Gx = 0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296;
// The y-coordinate of the generator
uint256 constant Gy = 0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5;
// p is the order of the abelian group Gp
uint256 constant p = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551;
