// SPDX-License-Identifier: agpl-3.0
pragma solidity ^0.8.10;

enum Rounding {
  UP,
  DOWN
}

/**
 * Simplified version of RayMath that instead of half-up rounding does explicit rounding in a specified direction.
 * This is needed to have a 4626 complient implementation, that always predictable rounds in favor of the vault / static a token.
 */
library RayMathExplicitRounding {
  uint256 internal constant RAY = 1e27;
  uint256 internal constant WAD_RAY_RATIO = 1e9;

  function rayMulRoundDown(uint256 a, uint256 b) internal pure returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00290000, 1037618708521) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00290001, 2) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00291000, a) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00291001, b) }
    if (a == 0 || b == 0) {
      return 0;
    }
    return (a * b) / RAY;
  }

  function rayMulRoundUp(uint256 a, uint256 b) internal pure returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff002a0000, 1037618708522) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff002a0001, 2) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff002a1000, a) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff002a1001, b) }
    if (a == 0 || b == 0) {
      return 0;
    }
    return ((a * b) + RAY - 1) / RAY;
  }

  function rayDivRoundDown(uint256 a, uint256 b) internal pure returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff002c0000, 1037618708524) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff002c0001, 2) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff002c1000, a) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff002c1001, b) }
    return (a * RAY) / b;
  }

  function rayDivRoundUp(uint256 a, uint256 b) internal pure returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff002d0000, 1037618708525) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff002d0001, 2) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff002d1000, a) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff002d1001, b) }
    return ((a * RAY) + b - 1) / b;
  }

  function rayToWadRoundDown(uint256 a) internal pure returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff002b0000, 1037618708523) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff002b0001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff002b1000, a) }
    return a / WAD_RAY_RATIO;
  }
}
