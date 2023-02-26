
pragma solidity ^0.8.10;

import {RewardsController} from '../../lib/aave-v3-periphery/contracts/rewards/RewardsController.sol';
import {RewardsDataTypes} from '../../lib/aave-v3-periphery/contracts/rewards/libraries/RewardsDataTypes.sol';

contract RewardsControllerHarness is RewardsController{


// function _getUserAssetBalances(address[] calldata assets, address user)
//     internal
//     view
//     override
//     returns (RewardsDataTypes.UserAssetBalance[] memory userAssetBalances){
        
//         revert();

//     }

function getavailableRewardsCount(address asset)
    external
    view
    returns (uint128)
  {
    return _assets[asset].availableRewardsCount;
  }


  function getFirstRewardsByAsset(address asset) external view  returns (address) {
    return _assets[asset].availableRewards[0];
  }

}