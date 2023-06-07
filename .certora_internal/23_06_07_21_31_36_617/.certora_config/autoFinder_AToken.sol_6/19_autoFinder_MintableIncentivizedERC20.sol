// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import {IAaveIncentivesController} from '../../../interfaces/IAaveIncentivesController.sol';
import {IPool} from '../../../interfaces/IPool.sol';
import { IncentivizedERC20 } from '/Users/dev1644/workspace/workspace-west/aave-certora/.certora_internal/23_06_07_21_31_36_617/.certora_sources/lib/aave-v3-core/contracts/protocol/tokenization/base/autoFinder_IncentivizedERC20.sol';

/**
 * @title MintableIncentivizedERC20
 * @author Aave
 * @notice Implements mint and burn functions for IncentivizedERC20
 */
abstract contract MintableIncentivizedERC20 is IncentivizedERC20 {
  /**
   * @dev Constructor.
   * @param pool The reference to the main Pool contract
   * @param name The name of the token
   * @param symbol The symbol of the token
   * @param decimals The number of decimals of the token
   */
  constructor(
    IPool pool,
    string memory name,
    string memory symbol,
    uint8 decimals
  ) IncentivizedERC20(pool, name, symbol, decimals) {
    // Intentionally left blank
  }

  /**
   * @notice Mints tokens to an account and apply incentives if defined
   * @param account The address receiving tokens
   * @param amount The amount of tokens to mint
   */
  function _mint(address account, uint128 amount) internal virtual {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff01010000, 1037618708737) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff01010001, 2) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff01011000, account) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff01011001, amount) }
    uint256 oldTotalSupply = _totalSupply;
    _totalSupply = oldTotalSupply + amount;

    uint128 oldAccountBalance = _userState[account].balance;
    _userState[account].balance = oldAccountBalance + amount;

    IAaveIncentivesController incentivesControllerLocal = _incentivesController;
    if (address(incentivesControllerLocal) != address(0)) {
      incentivesControllerLocal.handleAction(account, oldTotalSupply, oldAccountBalance);
    }
  }

  /**
   * @notice Burns tokens from an account and apply incentives if defined
   * @param account The account whose tokens are burnt
   * @param amount The amount of tokens to burn
   */
  function _burn(address account, uint128 amount) internal virtual {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff01020000, 1037618708738) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff01020001, 2) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff01021000, account) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff01021001, amount) }
    uint256 oldTotalSupply = _totalSupply;
    _totalSupply = oldTotalSupply - amount;

    uint128 oldAccountBalance = _userState[account].balance;
    _userState[account].balance = oldAccountBalance - amount;

    IAaveIncentivesController incentivesControllerLocal = _incentivesController;

    if (address(incentivesControllerLocal) != address(0)) {
      incentivesControllerLocal.handleAction(account, oldTotalSupply, oldAccountBalance);
    }
  }
}
