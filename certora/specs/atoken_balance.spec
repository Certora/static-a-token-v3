import "methods_base.spec"


using AToken as _AToken 
using DummyERC20_rewardToken as _DummyERC20_rewardToken
using DummyERC20_aTokenUnderlying as _DummyERC20_aTokenUnderlying 


/**
 * @dev Passed in job-id=`3bbb6bc807e44f399d05bc401e65284e`
 * Note that `UNDERLYING_ASSET_ADDRESS()` was unresolved.
 */


/////////////////// Methods ////////////////////////

    methods
    {
        // envfree
        // -------
        _AToken.balanceOf(address user) returns (uint256) envfree
        _AToken.UNDERLYING_ASSET_ADDRESS() returns (address) envfree

        // Permit
        permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => DISPATCHER(true)

        // AToken
        // ------
        mint(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
        burn(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
        getIncentivesController() returns (address) => CONSTANT
    }

///////////////// Properties ///////////////////////

    /**
    * @title User AToken balance is fixed
    * Interaction with `StaticAtokenLM` should not change a user's AToken balance,
    * except for the following methods:
    * - `withdraw`
    * - `deposit`
    * - `redeem`
    * - `mint`
    * - `metaDeposit`
    * - `metaWithdraw`
    *
    * Note. Rewards methods are special cases handled in other rules below.
    *
    * Rules passed (with rule sanity): job-id=`5fdaf5eeaca249e584c2eef1d66d73c7`
    *
    * Note. `UNDERLYING_ASSET_ADDRESS()` was unresolved!
    */
    rule aTokenBalanceIsFixed(method f) filtered {
        // Exclude balance changing methods
        f -> (f.selector != deposit(uint256,address).selector) &&
            (f.selector != deposit(uint256,address,uint16,bool).selector) &&
            (f.selector != withdraw(uint256,address,address).selector) &&
            (f.selector != redeem(uint256,address,address).selector) &&
            (f.selector != redeem(uint256,address,address,bool).selector) &&
            (f.selector != mint(uint256,address).selector) &&
            (f.selector != metaDeposit(
                address,address,uint256,uint16,bool,uint256,
                (address,address,uint256,uint256,uint8,bytes32,bytes32),
                (uint8, bytes32, bytes32)
            ).selector) &&
            (f.selector != metaWithdraw(
                address,address,uint256,uint256,bool,uint256,
                (uint8, bytes32, bytes32)
            ).selector) &&
            // Exclude reward related methods - these are handled below
            (f.selector != collectAndUpdateRewards(address).selector) &&
            (f.selector != claimRewardsOnBehalf(address,address,address[]).selector) &&
            (f.selector != claimSingleRewardOnBehalf(address,address,address).selector) &&
            (f.selector != claimRewardsToSelf(address[]).selector) &&
            (f.selector != claimRewards(address,address[]).selector)
    } {
        require _AToken == asset();
        require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;

        env e;

        // Limit sender
        require e.msg.sender != currentContract;
        require e.msg.sender != _AToken;

        uint256 preBalance = _AToken.balanceOf(e.msg.sender);

        calldataarg args;
        f(e, args);

        uint256 postBalance = _AToken.balanceOf(e.msg.sender);
        assert preBalance == postBalance, "aToken balance changed by static interaction";
    }

    rule aTokenBalanceIsFixed_for_collectAndUpdateRewards() {
        require _AToken == asset();
        require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;
        require _AToken != _DummyERC20_rewardToken;

        env e;

        // Limit sender
        require e.msg.sender != currentContract;
        require e.msg.sender != _AToken;
        require e.msg.sender != _DummyERC20_rewardToken;

        uint256 preBalance = _AToken.balanceOf(e.msg.sender);

        collectAndUpdateRewards(e, _DummyERC20_rewardToken);

        uint256 postBalance = _AToken.balanceOf(e.msg.sender);
        assert preBalance == postBalance, "aToken balance changed by collectAndUpdateRewards";
    }


    rule aTokenBalanceIsFixed_for_claimRewardsOnBehalf(address onBehalfOf, address receiver) {
        require _AToken == asset();
        require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;
        require _AToken != _DummyERC20_rewardToken;

        // Create a rewards array
        address[] _rewards;
        require _rewards[0] == _DummyERC20_rewardToken;
        require _rewards.length == 1;

        env e;

        // Limit sender
        require (
            (e.msg.sender != currentContract) &&
            (onBehalfOf != currentContract) &&
            (receiver != currentContract)
        );
        require (
            (e.msg.sender != _DummyERC20_rewardToken) &&
            (onBehalfOf != _DummyERC20_rewardToken) &&
            (receiver != _DummyERC20_rewardToken)
        );
        require (e.msg.sender != _AToken) && (onBehalfOf != _AToken) && (receiver != _AToken);

        uint256 preBalance = _AToken.balanceOf(e.msg.sender);

        claimRewardsOnBehalf(e, onBehalfOf, receiver, _rewards);

        uint256 postBalance = _AToken.balanceOf(e.msg.sender);
        assert preBalance == postBalance, "aToken balance changed by claimRewardsOnBehalf";
    }


    rule aTokenBalanceIsFixed_for_claimSingleRewardOnBehalf(address onBehalfOf, address receiver) {
        require _AToken == asset();
        require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;
        require _AToken != _DummyERC20_rewardToken;

        env e;

        // Limit sender
        require (
            (e.msg.sender != currentContract) &&
            (onBehalfOf != currentContract) &&
            (receiver != currentContract)
        );
        require (
            (e.msg.sender != _DummyERC20_rewardToken) &&
            (onBehalfOf != _DummyERC20_rewardToken) &&
            (receiver != _DummyERC20_rewardToken)
        );
        require (e.msg.sender != _AToken) && (onBehalfOf != _AToken) && (receiver != _AToken);

        uint256 preBalance = _AToken.balanceOf(e.msg.sender);

        claimSingleRewardOnBehalf(e, onBehalfOf, receiver, _DummyERC20_aTokenUnderlying);

        uint256 postBalance = _AToken.balanceOf(e.msg.sender);
        assert preBalance == postBalance, "aToken balance changed by claimSingleRewardOnBehalf";
    }


    rule aTokenBalanceIsFixed_for_claimRewardsToSelf() {
        require _AToken == asset();
        require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;
        require _AToken != _DummyERC20_rewardToken;

        // Create a rewards array
        address[] _rewards;
        require _rewards[0] == _DummyERC20_rewardToken;
        require _rewards.length == 1;

        env e;

        // Limit sender
        require e.msg.sender != currentContract;
        require e.msg.sender != _AToken;
        require e.msg.sender != _DummyERC20_rewardToken;

        uint256 preBalance = _AToken.balanceOf(e.msg.sender);

        claimRewardsToSelf(e, _rewards);

        uint256 postBalance = _AToken.balanceOf(e.msg.sender);
        assert preBalance == postBalance, "aToken balance changed by claimRewardsToSelf";
    }


    rule aTokenBalanceIsFixed_for_claimRewards(address receiver) {
        require _AToken == asset();
        require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;
        require _AToken != _DummyERC20_rewardToken;

        // Create a rewards array
        address[] _rewards;
        require _rewards[0] == _DummyERC20_rewardToken;
        require _rewards.length == 1;

        env e;

        // Limit sender
        require (e.msg.sender != currentContract) && (receiver != currentContract);
        require (
            (e.msg.sender != _DummyERC20_rewardToken) && (receiver != _DummyERC20_rewardToken)
        );
        require (e.msg.sender != _AToken) && (receiver != _AToken);

        uint256 preBalance = _AToken.balanceOf(e.msg.sender);

        claimRewards(e, receiver, _rewards);

        uint256 postBalance = _AToken.balanceOf(e.msg.sender);
        assert preBalance == postBalance, "aToken balance changed by claimRewards";
    }
