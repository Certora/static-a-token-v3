
pragma solidity ^0.8.10;

import {IPool} from '../../lib/aave-v3-core/contracts/interfaces/IPool.sol';
import {IRewardsController} from '../../lib/aave-v3-periphery/contracts/rewards/interfaces/IRewardsController.sol';
import {SymbolicLendingPoolL1} from './SymbolicLendingPoolL1.sol';


import {StaticATokenLM} from '../../src/StaticATokenLM.sol';

contract StaticATokenLMHarness is StaticATokenLM{

constructor(
    IPool pool,
    IRewardsController rewardsController
    ) StaticATokenLM(pool, rewardsController){}

}
