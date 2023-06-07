// SPDX-License-Identifier: agpl-3.0
pragma solidity ^0.8.10;

import { StaticATokenLM, StaticATokenErrors, IPool, IRewardsController, IERC20 } from '/Users/dev1644/workspace/workspace-west/aave-certora/.certora_internal/23_06_07_21_31_36_617/.certora_sources/src/autoFinder_StaticATokenLM.sol';
import {SymbolicLendingPool} from './pool/SymbolicLendingPool.sol';



contract StaticATokenLMHarness is StaticATokenLM{

    address internal _reward_A;
    address internal _reward_B;

    constructor(
        IPool pool,
        IRewardsController rewardsController
        ) StaticATokenLM(pool, rewardsController){}

    // returns the address of the underlying asset of the static aToken
    function getStaticATokenUnderlying() public view returns (address){assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00240000, 1037618708516) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00240001, 0) }
        return _aTokenUnderlying;
    }

    // returns the address of the i-th reward token in the reward tokens list maintained by the static aToken
    function getRewardToken(uint256 i) external view returns (address) {
        return _rewardTokens[i];
    }
    
    // returns the length of the reward tokens list maintained by the static aToken
    function getRewardTokensLength() external view returns (uint256) {
        return _rewardTokens.length;
    }

    // returns a user's reward index on last interaction for a given reward
    function getRewardsIndexOnLastInteraction(address user, address reward)
    external view returns (uint128) {
        UserRewardsData memory currentUserRewardsData = _userRewardsData[user][reward];
        return currentUserRewardsData.rewardsIndexOnLastInteraction;
    }

    // returns the reward's index value on last update
    function getLastUpdatedIndex(address reward) public view returns (uint248) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00150000, 1037618708501) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00150001, 1) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00151000, reward) }
        return _startIndex[reward].lastUpdatedIndex;
    }

    // claims rewards for a user on the static aToken.
    // the method builds the rewards array with a single reward and calls the internal claim function with it
    function claimSingleRewardOnBehalf(
        address onBehalfOf,
        address receiver,
        address reward
    ) external 
    {
        require (reward == _reward_A);
        address[] memory rewards = new address[](1);
        rewards[0] = _reward_A;

        // @MM - think of the best way to get rid of this require
        require(
            msg.sender == onBehalfOf ||
            msg.sender == INCENTIVES_CONTROLLER.getClaimer(onBehalfOf),
        StaticATokenErrors.INVALID_CLAIMER
        );
        _claimRewardsOnBehalf(onBehalfOf, receiver, rewards);
    }

    // claims rewards for a user on the static aToken.
    // the method builds the rewards array with 2 identical rewards and calls the internal claim function with it
    function claimDoubleRewardOnBehalfSame(
        address onBehalfOf,
        address receiver,
        address reward
    ) external 
    {
        require (reward == _reward_A);
        address[] memory rewards = new address[](2);
        rewards[0] = _reward_A;
        rewards[1] = _reward_A;

        require(
            msg.sender == onBehalfOf ||
            msg.sender == INCENTIVES_CONTROLLER.getClaimer(onBehalfOf),
        StaticATokenErrors.INVALID_CLAIMER
        );
        _claimRewardsOnBehalf(onBehalfOf, receiver, rewards);

    }

}
