
pragma solidity ^0.8.10;

import {RewardsController, RewardsDataTypes} from 'aave-v3-periphery/contracts/rewards/RewardsController.sol';

contract RewardsControllerHarness is RewardsController{

constructor(address emissionManager) RewardsController(emissionManager) {}
function getAvailableRewardsCount(address asset)
    external
    view
    returns (uint128)
  {
    return _assets[asset].availableRewardsCount;
  }

/// @dev assume i < availableRewardsCount
  function getRewardsByAsset(address asset, uint128 i) external view  returns (address) {
    return _assets[asset].availableRewards[i];
  }
  function getAssetByIndex(uint256 i) external view  returns (address) {
    return  _assetsList[i];
  }
  function getAssetListLength() external view  returns (uint256) {
    return  _assetsList.length;
  }

function getUserAccruedReward(
    address user,
    address asset,
    address reward
  ) external view returns (uint256) {
    return _assets[asset].rewards[reward].usersData[user].accrued;
  }

}