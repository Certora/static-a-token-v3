import "methods_multi_reward.spec"


/////////////////// Methods ////////////////////////

/**
 * @dev Summarizing getCurrentRewardsIndex as constant, to speed up verification.
 */

    methods{
	    getCurrentRewardsIndex(address reward) returns (uint256) => CONSTANT
    }

///////////////// Definition ///////////////////////

    /// @title Set up a single reward token
    function single_RewardToken_setup() {
        require isRegisteredRewardToken(_rewardTokenA);
        require getRewardTokensLength() == 1;
    }


    /// @title Set up a single reward token for `_AToken` in the `INCENTIVES_CONTROLLER`
    function rewardsController_arbitrary_single_reward_setup() {
        require _RewardsController.getAvailableRewardsCount(_AToken) == 1;
        require _RewardsController.getRewardsByAsset(_AToken, 0) == _rewardTokenA;
    }

///////////////// Properties ///////////////////////

/// @dev Broke the rule into two cases to speed up verification

    /**
     * @title Claiming the same reward twice assuming sufficient rewards
     * Using an array with the same reward twice does not give more rewards,
     * assuming the contract has sufficient rewards.
     *
     * @dev Passed in job-id=`54de623f62eb4c95a343ee38834c6d16`
     */
    rule prevent_duplicate_reward_claiming_single_reward_sufficient() {
        single_RewardToken_setup();
        rewardsController_arbitrary_single_reward_setup();

        env e;
        require e.msg.sender != currentContract;  // Cannot claim to contract

        uint256 initialBalance = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 claimable = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

        // Ensure contract has sufficient rewards
        require _rewardTokenA.balanceOf(currentContract) >= claimable;

        // Duplicate claim
        claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenA);
        
        uint256 duplicateClaimBalance = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 diff = duplicateClaimBalance - initialBalance;
        uint256 unclaimed = getUnclaimedRewards(e.msg.sender, _rewardTokenA);

        assert diff + unclaimed <= claimable, "Duplicate claim changes rewards";
    }

    /**
     * @title Claiming the same reward twice assuming insufficient rewards
     * Using an array with the same reward twice does not give more rewards,
     * assuming the contract does not have sufficient rewards.
     *
     * @dev Passed in job-id=`54de623f62eb4c95a343ee38834c6d16`
     */
    rule prevent_duplicate_reward_claiming_single_reward_insufficient() {
        single_RewardToken_setup();
        rewardsController_arbitrary_single_reward_setup();

        env e;
        require e.msg.sender != currentContract;  // Cannot claim to contract

        uint256 initialBalance = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 claimable = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

        // Ensure contract does not have sufficient rewards
        require _rewardTokenA.balanceOf(currentContract) < claimable;

        // Duplicate claim
        claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenA);
        
        uint256 duplicateClaimBalance = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 diff = duplicateClaimBalance - initialBalance;
        uint256 unclaimed = getUnclaimedRewards(e.msg.sender, _rewardTokenA);

        assert diff + unclaimed <= claimable, "Duplicate claim changes rewards";
    }
