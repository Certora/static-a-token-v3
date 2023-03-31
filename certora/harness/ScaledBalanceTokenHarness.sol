
pragma solidity ^0.8.10;

import {IPool} from '../munged/lib/aave-v3-core/contracts/interfaces/IPool.sol';
import {ScaledBalanceTokenBase} from '../munged/lib/aave-v3-core/contracts/protocol/tokenization/base/ScaledBalanceTokenBase.sol';


contract ScaledBalanceTokenHarness is  ScaledBalanceTokenBase{

constructor(
    IPool pool,
    string memory name,
    string memory symbol,
    uint8 decimals
  ) ScaledBalanceTokenBase(pool, name, symbol, decimals) {}

}