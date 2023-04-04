import "methods_base.spec"


using AToken as _AToken 
using DummyERC20_rewardToken as _DummyERC20_rewardToken
using DummyERC20_aTokenUnderlying as _DummyERC20_aTokenUnderlying 
using RewardsControllerHarness as _RewardsController
using TransferStrategyHarness as _TransferStrategyHarness

/////////////////// Methods ////////////////////////

    methods
    {
        // envfree
        // -------
        getUnclaimedRewards(address, address) returns (uint256) envfree
        rewardTokens() returns (address[]) envfree
        isRegisteredRewardToken(address) returns (bool) envfree
        
        // Getters from munged/harness
        getRewardTokensLength() returns (uint256) envfree 
        getRewardToken(uint256) returns (address) envfree

        // AToken
        _AToken.UNDERLYING_ASSET_ADDRESS() returns (address) envfree

        // Reward token
        _DummyERC20_rewardToken.balanceOf(address) returns (uint256) envfree
        _DummyERC20_rewardToken.totalSupply() returns (uint256) envfree

        // RewardsController
        _RewardsController.getAvailableRewardsCount(address) returns (uint128) envfree
        _RewardsController.getRewardsByAsset(address, uint128) returns (address) envfree
        _RewardsController.getAssetListLength() returns (uint256) envfree
        _RewardsController.getAssetByIndex(uint256) returns (address) envfree

        // Permit
        // ------
        permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => NONDET

        // AToken
        // ------
        mint(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
        burn(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
    }

///////////////// Definition ///////////////////////

    /**
    * @title Single reward setup
    * Setup the `StaticATokenLM`'s rewards so they contain a single reward token
    * which is` _DummyERC20_rewardToken`.
    */
    function single_RewardToken_setup() {
        // @MM - reminder to re-examine the first check
		// @SH - current version in this branch does not change anything in this regard
        // require isRegisteredRewardToken(_DummyERC20_rewardToken);
        require getRewardTokensLength() == 1;
        require getRewardToken(0) == _DummyERC20_rewardToken;
    }


    /**
    * @title Single reward setup in RewardsController
    * Sets (in `_RewardsController`) the first reward for `_AToken` as
    * `_DummyERC20_rewardToken`.
    */
    function rewardsController_reward_setup() {
        require _RewardsController.getAvailableRewardsCount(_AToken) > 0;
        require _RewardsController.getRewardsByAsset(_AToken, 0) == _DummyERC20_rewardToken;
    }

///////////////// Properties ///////////////////////

    /**
    * @title Rewards claiming when sufficient rewards exist
    * Ensures rewards are updated correctly after claiming, when there are enough
    * reward funds.
    *
    * @dev Passed in job-id=`655ba8737ada43efab71eaabf8d41096`
    */
    rule rewardsConsistencyWhenSufficientRewardsExist() {
        // Assuming single reward
        single_RewardToken_setup();

        // Create a rewards array
        address[] _rewards;
        require _rewards[0] == _DummyERC20_rewardToken;
        require _rewards.length == 1;

        env e;
        require e.msg.sender != currentContract;  // Cannot claim to contract
        uint256 rewardsBalancePre = _DummyERC20_rewardToken.balanceOf(e.msg.sender);
        uint256 claimablePre = getClaimableRewards(e, e.msg.sender, _DummyERC20_rewardToken);

        // Ensure contract has sufficient rewards
        require _DummyERC20_rewardToken.balanceOf(currentContract) >= claimablePre;

        claimRewardsToSelf(e, _rewards);

        uint256 rewardsBalancePost = _DummyERC20_rewardToken.balanceOf(e.msg.sender);
        uint256 unclaimedPost = getUnclaimedRewards(e.msg.sender, _DummyERC20_rewardToken);
        uint256 claimablePost = getClaimableRewards(e, e.msg.sender, _DummyERC20_rewardToken);
        
        assert rewardsBalancePost >= rewardsBalancePre, "Rewards balance reduced after claim";
        uint256 rewardsGiven = rewardsBalancePost - rewardsBalancePre;
        assert claimablePre == rewardsGiven + unclaimedPost, "Rewards given unequal to claimable";
        assert claimablePost == unclaimedPost, "Claimable different from unclaimed";
        assert unclaimedPost == 0;  // Left last as this is an implementation detail
    }

    /**
    * @title Rewards claiming when rewards are insufficient
    /* Ensures rewards are updated correctly after claiming, when there aren't
    * enough funds.
    *
    * @dev Failed in previous version of the code: job-id=`274946aa85a247149c025df228c71bc1`.
    * Failure reported in: `https://github.com/bgd-labs/static-a-token-v3/issues/23`.
    * Passed after fix with rule-sanity in job-id=`32b981560c2c41eab24606daa7d38694`.
    */
    rule rewardsConsistencyWhenInsufficientRewards() {
        // Assuming single reward
        single_RewardToken_setup();

        env e;
        require e.msg.sender != currentContract;  // Cannot claim to contract
        require e.msg.sender != _TransferStrategyHarness;

        uint256 rewardsBalancePre = _DummyERC20_rewardToken.balanceOf(e.msg.sender);
        uint256 claimablePre = getClaimableRewards(e, e.msg.sender, _DummyERC20_rewardToken);

        // Ensure contract does not have sufficient rewards
        require _DummyERC20_rewardToken.balanceOf(currentContract) < claimablePre;

        claimSingleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _DummyERC20_rewardToken);

        uint256 rewardsBalancePost = _DummyERC20_rewardToken.balanceOf(e.msg.sender);
        uint256 unclaimedPost = getUnclaimedRewards(e.msg.sender, _DummyERC20_rewardToken);
        uint256 claimablePost = getClaimableRewards(e, e.msg.sender, _DummyERC20_rewardToken);
        
        assert rewardsBalancePost >= rewardsBalancePre, "Rewards balance reduced after claim";
        uint256 rewardsGiven = rewardsBalancePost - rewardsBalancePre;
        // Note, when `rewardsGiven` is 0 the unclaimed rewards are not updated
        assert (
            ( (rewardsGiven > 0) => (claimablePre == rewardsGiven + unclaimedPost) ) &&
            ( (rewardsGiven == 0) => (claimablePre == claimablePost) )
            ), "Claimable rewards changed unexpectedly";
    }


    /**
    * @title Only claiming rewards should reduce contract's total rewards balance
    * Only "claim reward" methods should cause the total rewards balance of
    * `StaticATokenLM` to decline. Note that `initialize`, `metaDeposit`
    * and `metaWithdraw` are filtered out. To avoid timeouts the rest of the
    * methods were split between several versions of this rule.
    *
    * WARNING: `metaDeposit` seems to be vacuous, i.e. **always** fails on a
    * require statement.
    *
    * @dev Passed with rule-sanity in job-id=`98beb842d5b94278ac4a9222249fb564`
    * 
    */
    rule rewardsTotalDeclinesOnlyByClaim(method f) filtered {
        // Filter out initialize
        f -> (f.selector != initialize(address, string, string).selector) &&
            // Exclude meta functions
            (f.selector != metaDeposit(
                address,address,uint256,uint16,bool,uint256,
                (address,address,uint256,uint256,uint8,bytes32,bytes32),
                (uint8, bytes32, bytes32)
            ).selector) &&
            (f.selector != metaWithdraw(
                address,address,uint256,uint256,bool,uint256,
                (uint8, bytes32, bytes32)
            ).selector) &&
            // Exclude methods that time out
            (f.selector != deposit(uint256,address).selector) &&
            (f.selector != deposit(uint256,address,uint16,bool).selector) &&
            (f.selector != redeem(uint256,address,address).selector) &&
            (f.selector != redeem(uint256,address,address,bool).selector) &&
            (f.selector != mint(uint256,address).selector)
    } {
        // Assuming single reward
        single_RewardToken_setup();
        rewardsController_reward_setup();

        require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;

        env e;
        require e.msg.sender != currentContract;
        uint256 preTotal = getTotalClaimableRewards(e, _DummyERC20_rewardToken);

        calldataarg args;
        f(e, args);

        uint256 postTotal = getTotalClaimableRewards(e, _DummyERC20_rewardToken);

        assert (postTotal < preTotal) => (
            (f.selector == claimRewardsOnBehalf(address, address, address[]).selector) ||
            (f.selector == claimRewards(address, address[]).selector) ||
            (f.selector == claimRewardsToSelf(address[]).selector) ||
            (f.selector == claimSingleRewardOnBehalf(address,address,address).selector)
        ), "Total rewards decline not due to claim";
    }

    /// @dev Passed with rule-sanity in job-id=`f71cabe338614768af9e119dea55b00e`
    rule rewardsTotalDeclinesOnlyByClaim_timedout_methods(method f) filtered {
        // Include only the timed out methods, excluding redeem
        f -> (f.selector == deposit(uint256,address).selector) ||
            (f.selector == deposit(uint256,address,uint16,bool).selector) ||
            (f.selector == mint(uint256,address).selector)
    } {
        // Assuming single reward
        single_RewardToken_setup();
        rewardsController_reward_setup();

        require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;

        env e;
        require e.msg.sender != currentContract;
        uint256 preTotal = getTotalClaimableRewards(e, _DummyERC20_rewardToken);

        calldataarg args;
        f(e, args);

        uint256 postTotal = getTotalClaimableRewards(e, _DummyERC20_rewardToken);

        assert (postTotal < preTotal) => (
            (f.selector == claimRewardsOnBehalf(address, address, address[]).selector) ||
            (f.selector == claimRewards(address, address[]).selector) ||
            (f.selector == claimRewardsToSelf(address[]).selector) ||
            (f.selector == claimSingleRewardOnBehalf(address,address,address).selector)
        ), "Total rewards decline not due to claim";
    }

	/**
	 * @dev Passed in job-id=`06a3d30b577b4a8a8d26182e7486b065`
	 * using `--settings -t=7200,-mediumTimeout=40,-depth=7`
	 */
    rule rewardsTotalDeclinesOnlyByClaim_redeem_methods(method f) filtered {
        // Include only the redeem timed out methods
        f -> (f.selector == redeem(uint256,address,address).selector) ||
            (f.selector == redeem(uint256,address,address,bool).selector)
    } {
        // Assuming single reward
        single_RewardToken_setup();
        rewardsController_reward_setup();

        require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;

        env e;
        require e.msg.sender != currentContract;
        uint256 preTotal = getTotalClaimableRewards(e, _DummyERC20_rewardToken);

        calldataarg args;
        f(e, args);

        uint256 postTotal = getTotalClaimableRewards(e, _DummyERC20_rewardToken);

        assert (postTotal < preTotal) => (
            (f.selector == claimRewardsOnBehalf(address, address, address[]).selector) ||
            (f.selector == claimRewards(address, address[]).selector) ||
            (f.selector == claimRewardsToSelf(address[]).selector) ||
            (f.selector == claimSingleRewardOnBehalf(address,address,address).selector)
        ), "Total rewards decline not due to claim";
    }
