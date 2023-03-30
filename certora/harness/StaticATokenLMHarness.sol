
pragma solidity ^0.8.10;

import {IPool} from 'aave-v3-core/contracts/interfaces/IPool.sol';
import {IRewardsController} from 'aave-v3-periphery/contracts/rewards/interfaces/IRewardsController.sol';
import {SymbolicLendingPoolL1} from './SymbolicLendingPoolL1.sol';

import {StaticATokenErrors} from '../munged/src/StaticATokenErrors.sol';
import {StaticATokenLM} from '../munged/src/StaticATokenLM.sol';

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

  function getrewardsIndexOnLastInteraction(address user, address reward)
  external view returns (uint128) {
    UserRewardsData memory currentUserRewardsData = _userRewardsData[user][reward];
    return currentUserRewardsData.rewardsIndexOnLastInteraction;
  }

  
  function getlastUpdatedIndex(address reward) external view returns (uint248){
    return _startIndex[reward].lastUpdatedIndex;
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

}
