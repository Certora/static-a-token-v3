import "methods_multi_reward.spec"


/////////////////// Methods ////////////////////////

/**
 * @dev Summarizing getCurrentRewardsIndex as constant per reward, to speed up
 * verification.
 */

    methods{
        getCurrentRewardsIndex(address reward) returns (uint256) => getCurrentRewardsIndex_summary(reward)
    }

///////////////// Definition ///////////////////////

    /// @title Used for summarizing `getCurrentRewardsIndex`
    ghost mapping(address => uint256) _rewards_indexes;

    /// @title Summarizes `getCurrentRewardsIndex` as constant per reward
    function getCurrentRewardsIndex_summary(address reward) returns uint256 {
        return _rewards_indexes[reward];
    }

    /// @title Two rewards setup
    function dual_RewardToken_setup() {
        require _rewardTokenA != _rewardTokenB;
        require isRegisteredRewardToken(_rewardTokenA);
        require isRegisteredRewardToken(_rewardTokenB);
        require getRewardTokensLength() == 2;
    }

    /// @title Two rewards setup for `_AToken` in the `INCENTIVES_CONTROLLER`
    function rewardsController_arbitrary_dual_reward_setup() {
        require _RewardsController.getAvailableRewardsCount(_AToken) == 2;
        require _RewardsController.getRewardsByAsset(_AToken, 0) == _rewardTokenA;
        require _RewardsController.getRewardsByAsset(_AToken, 1) == _rewardTokenB;
    }

///////////////// Properties ///////////////////////

    /**
     * @title Claiming two rewards at once
     * Claiming two reward tokens in one array is the same as claiming each one separately.
     * This is based on two rules from `rewardsPreserve.spec`:
     * `rewardsConsistencyWhenSufficientRewardsExist` and `rewardsConsistencyWhenInsufficientRewards`.
     *
     * @dev Previous version passed without rule_sanity in: job-id=`3f8335e5b0a046b384062b5899337b00`
     * Previous version manual sanity test: job-id=`7987b62318ed431997b24948af9fcc23`
     */
    rule dual_reward_claiming() {
        dual_RewardToken_setup();
        rewardsController_arbitrary_dual_reward_setup();

        env e;
        require e.msg.sender != currentContract;  // Cannot claim to contract

        uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

        uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);
        
        claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
        
        uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 diffA = postBalanceA - initialBalanceA;
        uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
        uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

        uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 diffB = postBalanceB - initialBalanceB;
        uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
        uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

        assert (
            ( (diffA > 0) => (diffA + unclaimedA == claimableA) ) &&
            (( diffA == 0) => (claimableA == claimablePostA) )
        ), "Two rewards claim changes reward A";
        assert (
            ( (diffB > 0) => (diffB + unclaimedB == claimableB) ) &&
            (( diffB == 0) => (claimableB == claimablePostB) )
        ), "Two rewards claim changes reward B";
    }


    /**
     * @dev Passed in: job-id=`898ad8ac9ae247248867b8a42edddebb`
     * using: `--settings -t=3600,-mediumTimeout=50,-depth=7`
     */
    rule dual_reward_claiming_assuming_sufficient_rewards() {
        dual_RewardToken_setup();
        rewardsController_arbitrary_dual_reward_setup();

        env e;
        require e.msg.sender != currentContract;  // Cannot claim to contract

        uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

        uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);
        
        // Ensure contract has sufficient rewards
        require _rewardTokenA.balanceOf(currentContract) >= claimableA;
        require _rewardTokenB.balanceOf(currentContract) >= claimableB;

        claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
        
        uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 diffA = postBalanceA - initialBalanceA;
        uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
        uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

        uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 diffB = postBalanceB - initialBalanceB;
        uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
        uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

        assert (diffA > 0) => (diffA + unclaimedA == claimableA), "Two rewards claim changes reward A";
        assert (diffB > 0) => (diffB + unclaimedB == claimableB), "Two rewards claim changes reward B";
    }

    rule manual_sanity_dual_reward_claiming_assuming_sufficient_rewards() {
        dual_RewardToken_setup();
        rewardsController_arbitrary_dual_reward_setup();

        env e;
        require e.msg.sender != currentContract;  // Cannot claim to contract

        uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

        uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);
        
        // Ensure contract has sufficient rewards
        require _rewardTokenA.balanceOf(currentContract) >= claimableA;
        require _rewardTokenB.balanceOf(currentContract) >= claimableB;

        claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
        
        uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 diffA = postBalanceA - initialBalanceA;
        uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
        uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

        uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 diffB = postBalanceB - initialBalanceB;
        uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
        uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

        assert false;
    }


    /**
     * @dev Passed in: job-id=`3b17ee1dfee3420ba4eaa61cace2c278`
     * using: `--settings -t=3600,-mediumTimeout=50,-depth=7`
     */
    rule dual_reward_claiming_assuming_sufficientA_insufficientB() {
        dual_RewardToken_setup();
        rewardsController_arbitrary_dual_reward_setup();

        env e;
        require e.msg.sender != currentContract;  // Cannot claim to contract

        uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

        uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);
        
        // Ensure contract has sufficient/insufficient rewards
        require _rewardTokenA.balanceOf(currentContract) >= claimableA;
        require _rewardTokenB.balanceOf(currentContract) < claimableB;

        claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
        
        uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 diffA = postBalanceA - initialBalanceA;
        uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
        uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

        uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 diffB = postBalanceB - initialBalanceB;
        uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
        uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

        assert (diffA > 0) => (diffA + unclaimedA == claimableA), "Two rewards claim changes reward A";
        assert (
            ( (diffB > 0) => (diffB + unclaimedB == claimableB) ) &&
            (( diffB == 0) => (claimableB == claimablePostB) )
        ), "Two rewards claim changes reward B";
    }

    rule manual_sanity_dual_reward_claiming_assuming_sufficientA_insufficientB() {
        dual_RewardToken_setup();
        rewardsController_arbitrary_dual_reward_setup();

        env e;
        require e.msg.sender != currentContract;  // Cannot claim to contract

        uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

        uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);
        
        // Ensure contract has sufficient/insufficient rewards
        require _rewardTokenA.balanceOf(currentContract) >= claimableA;
        require _rewardTokenB.balanceOf(currentContract) < claimableB;

        claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
        
        uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 diffA = postBalanceA - initialBalanceA;
        uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
        uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

        uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 diffB = postBalanceB - initialBalanceB;
        uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
        uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

        assert false;
    }


    /**
     * @dev Passed in: job-id=`f0e8ae865b4642f1bbed174490b4ea3d`
     * using: `--settings -t=7200,-mediumTimeout=100,-depth=10`
     */
    rule dual_reward_claiming_assuming_insufficientA_sufficientB() {
        dual_RewardToken_setup();
        rewardsController_arbitrary_dual_reward_setup();

        env e;
        require e.msg.sender != currentContract;  // Cannot claim to contract

        uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

        uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

        // Ensure contract has sufficient/insufficient rewards
        require _rewardTokenA.balanceOf(currentContract) < claimableA;
        require _rewardTokenB.balanceOf(currentContract) >= claimableB;

        claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
        
        uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 diffA = postBalanceA - initialBalanceA;
        uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
        uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

        uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 diffB = postBalanceB - initialBalanceB;
        uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
        uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

        assert (
            ( (diffA > 0) => (diffA + unclaimedA == claimableA) ) &&
            (( diffA == 0) => (claimableA == claimablePostA) )
        ), "Two rewards claim changes reward A";
        assert (diffB > 0) => (diffB + unclaimedB == claimableB), "Two rewards claim changes reward B";
    }

    rule manual_sanity_dual_reward_claiming_assuming_insufficientA_sufficientB() {
        dual_RewardToken_setup();
        rewardsController_arbitrary_dual_reward_setup();

        env e;
        require e.msg.sender != currentContract;  // Cannot claim to contract

        uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

        uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

        // Ensure contract has sufficient/insufficient rewards
        require _rewardTokenA.balanceOf(currentContract) < claimableA;
        require _rewardTokenB.balanceOf(currentContract) >= claimableB;

        claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
        
        uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 diffA = postBalanceA - initialBalanceA;
        uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
        uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

        uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 diffB = postBalanceB - initialBalanceB;
        uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
        uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

        assert false;
    }


    /**
     * @dev Passed (without rule_sanity) in: job-id=39a25c6f9785451b8eaa587a4184bbf4
     */
    rule dual_reward_claiming_insufficient_rewards_both() {
        dual_RewardToken_setup();
        rewardsController_arbitrary_dual_reward_setup();

        env e;
        require e.msg.sender != currentContract;  // Cannot claim to contract

        uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

        uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

        // Ensure contracts have insufficient rewards
        require _rewardTokenA.balanceOf(currentContract) < claimableA;
        require _rewardTokenB.balanceOf(currentContract) < claimableB;
        
        claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
        
        uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 diffA = postBalanceA - initialBalanceA;
        uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
        uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

        uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 diffB = postBalanceB - initialBalanceB;
        uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
        uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

        assert (
            ( (diffA > 0) => (diffA + unclaimedA == claimableA) ) &&
            (( diffA == 0) => (claimableA == claimablePostA) )
        ), "Two rewards claim changes reward A";
        assert (
            ( (diffB > 0) => (diffB + unclaimedB == claimableB) ) &&
            (( diffB == 0) => (claimableB == claimablePostB) )
        ), "Two rewards claim changes reward B";
    }

    rule manual_sanity_dual_reward_claiming_insufficient_rewards_both() {
        dual_RewardToken_setup();
        rewardsController_arbitrary_dual_reward_setup();

        env e;
        require e.msg.sender != currentContract;  // Cannot claim to contract

        uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

        uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

        // Ensure contracts have insufficient rewards
        require _rewardTokenA.balanceOf(currentContract) < claimableA;
        require _rewardTokenB.balanceOf(currentContract) < claimableB;
        
        claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
        
        uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
        uint256 diffA = postBalanceA - initialBalanceA;
        uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
        uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

        uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
        uint256 diffB = postBalanceB - initialBalanceB;
        uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
        uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

        assert false;
    }
