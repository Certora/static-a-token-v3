
pragma solidity ^0.8.10;

import {RewardsDistributor} from '../../lib/aave-v3-periphery/contracts/rewards/RewardsDistributor.sol';
import {RewardsDataTypes} from '../../lib/aave-v3-periphery/contracts/rewards/libraries/RewardsDataTypes.sol';

contract RewardsDistributorHarness is RewardsDistributor{


function _getUserAssetBalances(address[] calldata assets, address user)
    internal
    view
    override
    returns (RewardsDataTypes.UserAssetBalance[] memory userAssetBalances){
        
        revert();

    }

}