// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts v4.4.1 (utils/math/SafeCast.sol)
pragma solidity 0.8.10;

/**
 * @dev Wrappers over Solidity's uintXX/intXX casting operators with added overflow
 * checks.
 *
 * Downcasting from uint256/int256 in Solidity does not revert on overflow. This can
 * easily result in undesired exploitation or bugs, since developers usually
 * assume that overflows raise errors. `SafeCast` restores this intuition by
 * reverting the transaction when such an operation overflows.
 *
 * Using this library instead of the unchecked operations eliminates an entire
 * class of bugs, so it's recommended to use it always.
 *
 * Can be combined with {SafeMath} and {SignedSafeMath} to extend it to smaller types, by performing
 * all math on `uint256` and `int256` and then downcasting.
 */
library SafeCast {
  /**
   * @dev Returns the downcasted uint224 from uint256, reverting on
   * overflow (when the input is greater than largest uint224).
   *
   * Counterpart to Solidity's `uint224` operator.
   *
   * Requirements:
   *
   * - input must fit into 224 bits
   */
  function toUint224(uint256 value) internal pure returns (uint224) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00c70000, 1037618708679) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00c70001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00c71000, value) }
    require(value <= type(uint224).max, "SafeCast: value doesn't fit in 224 bits");
    return uint224(value);
  }

  /**
   * @dev Returns the downcasted uint128 from uint256, reverting on
   * overflow (when the input is greater than largest uint128).
   *
   * Counterpart to Solidity's `uint128` operator.
   *
   * Requirements:
   *
   * - input must fit into 128 bits
   */
  function toUint128(uint256 value) internal pure returns (uint128) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00c80000, 1037618708680) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00c80001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00c81000, value) }
    require(value <= type(uint128).max, "SafeCast: value doesn't fit in 128 bits");
    return uint128(value);
  }

  /**
   * @dev Returns the downcasted uint96 from uint256, reverting on
   * overflow (when the input is greater than largest uint96).
   *
   * Counterpart to Solidity's `uint96` operator.
   *
   * Requirements:
   *
   * - input must fit into 96 bits
   */
  function toUint96(uint256 value) internal pure returns (uint96) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00ca0000, 1037618708682) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00ca0001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00ca1000, value) }
    require(value <= type(uint96).max, "SafeCast: value doesn't fit in 96 bits");
    return uint96(value);
  }

  /**
   * @dev Returns the downcasted uint64 from uint256, reverting on
   * overflow (when the input is greater than largest uint64).
   *
   * Counterpart to Solidity's `uint64` operator.
   *
   * Requirements:
   *
   * - input must fit into 64 bits
   */
  function toUint64(uint256 value) internal pure returns (uint64) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00cb0000, 1037618708683) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00cb0001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00cb1000, value) }
    require(value <= type(uint64).max, "SafeCast: value doesn't fit in 64 bits");
    return uint64(value);
  }

  /**
   * @dev Returns the downcasted uint32 from uint256, reverting on
   * overflow (when the input is greater than largest uint32).
   *
   * Counterpart to Solidity's `uint32` operator.
   *
   * Requirements:
   *
   * - input must fit into 32 bits
   */
  function toUint32(uint256 value) internal pure returns (uint32) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00c90000, 1037618708681) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00c90001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00c91000, value) }
    require(value <= type(uint32).max, "SafeCast: value doesn't fit in 32 bits");
    return uint32(value);
  }

  /**
   * @dev Returns the downcasted uint16 from uint256, reverting on
   * overflow (when the input is greater than largest uint16).
   *
   * Counterpart to Solidity's `uint16` operator.
   *
   * Requirements:
   *
   * - input must fit into 16 bits
   */
  function toUint16(uint256 value) internal pure returns (uint16) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00cc0000, 1037618708684) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00cc0001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00cc1000, value) }
    require(value <= type(uint16).max, "SafeCast: value doesn't fit in 16 bits");
    return uint16(value);
  }

  /**
   * @dev Returns the downcasted uint8 from uint256, reverting on
   * overflow (when the input is greater than largest uint8).
   *
   * Counterpart to Solidity's `uint8` operator.
   *
   * Requirements:
   *
   * - input must fit into 8 bits.
   */
  function toUint8(uint256 value) internal pure returns (uint8) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00cd0000, 1037618708685) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00cd0001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00cd1000, value) }
    require(value <= type(uint8).max, "SafeCast: value doesn't fit in 8 bits");
    return uint8(value);
  }

  /**
   * @dev Converts a signed int256 into an unsigned uint256.
   *
   * Requirements:
   *
   * - input must be greater than or equal to 0.
   */
  function toUint256(int256 value) internal pure returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00ce0000, 1037618708686) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00ce0001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00ce1000, value) }
    require(value >= 0, 'SafeCast: value must be positive');
    return uint256(value);
  }

  /**
   * @dev Returns the downcasted int128 from int256, reverting on
   * overflow (when the input is less than smallest int128 or
   * greater than largest int128).
   *
   * Counterpart to Solidity's `int128` operator.
   *
   * Requirements:
   *
   * - input must fit into 128 bits
   *
   * _Available since v3.1._
   */
  function toInt128(int256 value) internal pure returns (int128) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00cf0000, 1037618708687) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00cf0001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00cf1000, value) }
    require(
      value >= type(int128).min && value <= type(int128).max,
      "SafeCast: value doesn't fit in 128 bits"
    );
    return int128(value);
  }

  /**
   * @dev Returns the downcasted int64 from int256, reverting on
   * overflow (when the input is less than smallest int64 or
   * greater than largest int64).
   *
   * Counterpart to Solidity's `int64` operator.
   *
   * Requirements:
   *
   * - input must fit into 64 bits
   *
   * _Available since v3.1._
   */
  function toInt64(int256 value) internal pure returns (int64) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d00000, 1037618708688) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d00001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d01000, value) }
    require(
      value >= type(int64).min && value <= type(int64).max,
      "SafeCast: value doesn't fit in 64 bits"
    );
    return int64(value);
  }

  /**
   * @dev Returns the downcasted int32 from int256, reverting on
   * overflow (when the input is less than smallest int32 or
   * greater than largest int32).
   *
   * Counterpart to Solidity's `int32` operator.
   *
   * Requirements:
   *
   * - input must fit into 32 bits
   *
   * _Available since v3.1._
   */
  function toInt32(int256 value) internal pure returns (int32) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d10000, 1037618708689) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d10001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d11000, value) }
    require(
      value >= type(int32).min && value <= type(int32).max,
      "SafeCast: value doesn't fit in 32 bits"
    );
    return int32(value);
  }

  /**
   * @dev Returns the downcasted int16 from int256, reverting on
   * overflow (when the input is less than smallest int16 or
   * greater than largest int16).
   *
   * Counterpart to Solidity's `int16` operator.
   *
   * Requirements:
   *
   * - input must fit into 16 bits
   *
   * _Available since v3.1._
   */
  function toInt16(int256 value) internal pure returns (int16) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d20000, 1037618708690) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d20001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d21000, value) }
    require(
      value >= type(int16).min && value <= type(int16).max,
      "SafeCast: value doesn't fit in 16 bits"
    );
    return int16(value);
  }

  /**
   * @dev Returns the downcasted int8 from int256, reverting on
   * overflow (when the input is less than smallest int8 or
   * greater than largest int8).
   *
   * Counterpart to Solidity's `int8` operator.
   *
   * Requirements:
   *
   * - input must fit into 8 bits.
   *
   * _Available since v3.1._
   */
  function toInt8(int256 value) internal pure returns (int8) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d30000, 1037618708691) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d30001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d31000, value) }
    require(
      value >= type(int8).min && value <= type(int8).max,
      "SafeCast: value doesn't fit in 8 bits"
    );
    return int8(value);
  }

  /**
   * @dev Converts an unsigned uint256 into a signed int256.
   *
   * Requirements:
   *
   * - input must be less than or equal to maxInt256.
   */
  function toInt256(uint256 value) internal pure returns (int256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d40000, 1037618708692) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d40001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d41000, value) }
    // Note: Unsafe cast below is okay because `type(int256).max` is guaranteed to be positive
    require(value <= uint256(type(int256).max), "SafeCast: value doesn't fit in an int256");
    return int256(value);
  }
}
