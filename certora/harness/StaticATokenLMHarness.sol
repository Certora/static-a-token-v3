// SPDX-License-Identifier: agpl-3.0
pragma solidity ^0.8.10;

import {StaticATokenLM, StaticATokenErrors,  IPool, IRewardsController, IERC20} from '../munged/src/StaticATokenLM.sol';
import {SymbolicLendingPoolL1} from './SymbolicLendingPoolL1.sol';



contract StaticATokenLMHarness is StaticATokenLM{
    

constructor(
    IPool pool,
    IRewardsController rewardsController
    ) StaticATokenLM(pool, rewardsController){}


    function getULBalanceOf(address recipient) public returns (uint256 balance){
        balance = IERC20(_aTokenUnderlying).balanceOf(recipient);
    }

    function getATokenBalanceOf(address recipient) public returns (uint256 balance){
        balance = _aToken.balanceOf(recipient);
    }
    

    function assetsTotal(address account) public returns (uint256 assets){
        assets = _aToken.balanceOf(account) + IERC20(_aTokenUnderlying).balanceOf(account);

    }

    function getStaticATokenUnderlying() public view returns (address){
        return _aTokenUnderlying;
    }
    
    
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

  function _mintWrapper(address to, uint256 amount) external {
    _mint(to, amount);

  function claimDoubleRewardOnBehalf(
    address onBehalfOf,
    address receiver,
    address reward0,
    address reward1
  ) external 
  {

    address[] memory rewards = new address[](2);
    rewards[0] = address(reward0);
    rewards[1] = address(reward1);

      require(
        msg.sender == onBehalfOf ||
        msg.sender == INCENTIVES_CONTROLLER.getClaimer(onBehalfOf),
      StaticATokenErrors.INVALID_CLAIMER
    );
    _claimRewardsOnBehalf(onBehalfOf, receiver, rewards);

  }

  function getUserRewardsData(address user, address reward)
  external view
  returns (uint128) {
    UserRewardsData memory currentUserRewardsData = _userRewardsData[user][
      reward
    ];
    return currentUserRewardsData.rewardsIndexOnLastInteraction;
  }

}
