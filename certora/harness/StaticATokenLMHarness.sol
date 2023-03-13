
pragma solidity ^0.8.10;

import {IPool} from 'aave-v3-core/contracts/interfaces/IPool.sol';

import {IRewardsController} from 'aave-v3-periphery/contracts/rewards/interfaces/IRewardsController.sol';
import {SymbolicLendingPoolL1} from './SymbolicLendingPoolL1.sol';

import {StaticATokenErrors} from '../../src/StaticATokenErrors.sol';
import {StaticATokenLM} from '../../src/StaticATokenLM.sol';

contract StaticATokenLMHarness is StaticATokenLM{

constructor(
    IPool pool,
    IRewardsController rewardsController
    ) StaticATokenLM(pool, rewardsController){}


    
  function getRewardTokensLength() external view returns (uint256) {
    return _rewardTokens.length;
  }

  function getRewardToken(uint256 i) external view returns (address) {
    return _rewardTokens[i];
  }


  function claimSingleRewardOnBehalf(
    address onBehalfOf,
    address receiver,
    address reward
  ) external 
  {

    address[] memory rewards = new address[](1);
    rewards[0] = address(reward);

      require(
        msg.sender == onBehalfOf ||
        msg.sender == INCENTIVES_CONTROLLER.getClaimer(onBehalfOf),
      StaticATokenErrors.INVALID_CLAIMER
    );
    _claimRewardsOnBehalf(onBehalfOf, receiver, rewards);
    
  }
  ///@inheritdoc IStaticATokenLM

}