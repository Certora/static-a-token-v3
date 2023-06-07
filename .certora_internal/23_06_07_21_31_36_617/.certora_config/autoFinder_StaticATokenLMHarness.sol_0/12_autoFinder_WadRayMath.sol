// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

/**
 * @title WadRayMath library
 * @author Aave
 * @notice Provides functions to perform calculations with Wad and Ray units
 * @dev Provides mul and div function for wads (decimal numbers with 18 digits of precision) and rays (decimal numbers
 * with 27 digits of precision)
 * @dev Operations are rounded. If a value is >=.5, will be rounded up, otherwise rounded down.
 */
library WadRayMath {
  // HALF_WAD and HALF_RAY expressed with extended notation as constant with operations are not supported in Yul assembly
  uint256 internal constant WAD = 1e18;
  uint256 internal constant HALF_WAD = 0.5e18;

  uint256 internal constant RAY = 1e27;
  uint256 internal constant HALF_RAY = 0.5e27;

  uint256 internal constant WAD_RAY_RATIO = 1e9;

  /**
   * @dev Multiplies two wad, rounding half up to the nearest wad
   * @dev assembly optimized for improved gas savings, see https://twitter.com/transmissions11/status/1451131036377571328
   * @param a Wad
   * @param b Wad
   * @return c = a*b, in wad
   */
  function wadMul(uint256 a, uint256 b) internal pure returns (uint256 c) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005a0000, 1037618708570) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005a0001, 2) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005a1000, a) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005a1001, b) }
    // to avoid overflow, a <= (type(uint256).max - HALF_WAD) / b
    assembly {
      if iszero(or(iszero(b), iszero(gt(a, div(sub(not(0), HALF_WAD), b))))) {
        revert(0, 0)
      }

      c := div(add(mul(a, b), HALF_WAD), WAD)
    }
  }

  /**
   * @dev Divides two wad, rounding half up to the nearest wad
   * @dev assembly optimized for improved gas savings, see https://twitter.com/transmissions11/status/1451131036377571328
   * @param a Wad
   * @param b Wad
   * @return c = a/b, in wad
   */
  function wadDiv(uint256 a, uint256 b) internal pure returns (uint256 c) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005b0000, 1037618708571) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005b0001, 2) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005b1000, a) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005b1001, b) }
    // to avoid overflow, a <= (type(uint256).max - halfB) / WAD
    assembly {
      if or(iszero(b), iszero(iszero(gt(a, div(sub(not(0), div(b, 2)), WAD))))) {
        revert(0, 0)
      }

      c := div(add(mul(a, WAD), div(b, 2)), b)
    }
  }

  /**
   * @notice Multiplies two ray, rounding half up to the nearest ray
   * @dev assembly optimized for improved gas savings, see https://twitter.com/transmissions11/status/1451131036377571328
   * @param a Ray
   * @param b Ray
   * @return c = a raymul b
   */
  function rayMul(uint256 a, uint256 b) internal pure returns (uint256 c) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005d0000, 1037618708573) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005d0001, 2) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005d1000, a) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005d1001, b) }
    // to avoid overflow, a <= (type(uint256).max - HALF_RAY) / b
    assembly {
      if iszero(or(iszero(b), iszero(gt(a, div(sub(not(0), HALF_RAY), b))))) {
        revert(0, 0)
      }

      c := div(add(mul(a, b), HALF_RAY), RAY)
    }
  }

  /**
   * @notice Divides two ray, rounding half up to the nearest ray
   * @dev assembly optimized for improved gas savings, see https://twitter.com/transmissions11/status/1451131036377571328
   * @param a Ray
   * @param b Ray
   * @return c = a raydiv b
   */
  function rayDiv(uint256 a, uint256 b) internal pure returns (uint256 c) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005e0000, 1037618708574) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005e0001, 2) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005e1000, a) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005e1001, b) }
    // to avoid overflow, a <= (type(uint256).max - halfB) / RAY
    assembly {
      if or(iszero(b), iszero(iszero(gt(a, div(sub(not(0), div(b, 2)), RAY))))) {
        revert(0, 0)
      }

      c := div(add(mul(a, RAY), div(b, 2)), b)
    }
  }

  /**
   * @dev Casts ray down to wad
   * @dev assembly optimized for improved gas savings, see https://twitter.com/transmissions11/status/1451131036377571328
   * @param a Ray
   * @return b = a converted to wad, rounded half up to the nearest wad
   */
  function rayToWad(uint256 a) internal pure returns (uint256 b) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005c0000, 1037618708572) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005c0001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005c1000, a) }
    assembly {
      b := div(a, WAD_RAY_RATIO)
      let remainder := mod(a, WAD_RAY_RATIO)
      if iszero(lt(remainder, div(WAD_RAY_RATIO, 2))) {
        b := add(b, 1)
      }
    }
  }

  /**
   * @dev Converts wad up to ray
   * @dev assembly optimized for improved gas savings, see https://twitter.com/transmissions11/status/1451131036377571328
   * @param a Wad
   * @return b = a converted in ray
   */
  function wadToRay(uint256 a) internal pure returns (uint256 b) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005f0000, 1037618708575) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005f0001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff005f1000, a) }
    // to avoid overflow, b/WAD_RAY_RATIO == a
    assembly {
      b := mul(a, WAD_RAY_RATIO)

      if iszero(eq(div(b, WAD_RAY_RATIO), a)) {
        revert(0, 0)
      }
    }
  }
}
