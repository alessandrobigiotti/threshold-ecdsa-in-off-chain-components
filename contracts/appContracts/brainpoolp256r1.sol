// SPDX-License-Identifier: Apache 2.0
pragma solidity >=0.8.0 <0.9.0;

// Auxiliary booleans to simplify the checks about the constant a
bool constant isZeroA = false;
bool constant isNegativeA = false;
bool constant isPositiveA = true;

// BRAINPOOLP256R1 domain parameters
// q is the order of the finite field Fq
uint256 constant q = 0xa9fb57dba1eea9bc3e660a909d838d726e3bf623d52620282013481d1f6e5377;
// The constant a of the curve
uint256 constant a = 0x7d5a0975fc2c3057eef67530417affe7fb8055c126dc5c6ce94a4b44f330b5d9;
// The constant b of the curve
uint256 constant b = 0x26dc5c6ce94a4b44f330b5d9bbd77cbf958416295cf7e1ce6bccdc18ff8c07b6;
// The x-coordinate of the generator
uint256 constant Gx = 0x8bd2aeb9cb7e57cb2c4b482ffc81b7afb9de27e1e3bd23c23a4453bd9ace3262;
// The y-coordinate of the generator
uint256 constant Gy = 0x547ef835c3dac4fd97f8461a14611dc9c27745132ded8e545c1d54c72f046997;
// p is the order of the abelian group Gp
uint256 constant p = 0xa9fb57dba1eea9bc3e660a909d838d718c397aa3b561a6f7901e0e82974856a7;
