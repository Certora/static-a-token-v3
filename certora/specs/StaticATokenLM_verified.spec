import "methods_base.spec"

/////////////////// Methods ////////////////////////

    methods
    {   
        permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => NONDET
        getIncentivesController() returns (address) => CONSTANT
        getRewardsList() returns (address[]) => NONDET
        //call by RewardsController.IncentivizedERC20.sol and also by StaticATokenLM.sol
        handleAction(address,uint256,uint256) => DISPATCHER(true)
    }

////////////////// FUNCTIONS //////////////////////

    /// @title Reward hook
    /// @notice allows a single reward
    //todo: allow 2 or 3 rewards
    hook Sload address reward _rewardTokens[INDEX  uint256 i] STORAGE {
        require reward == _DummyERC20_rewardToken;
    } 

    /// @title Sum of balances of StaticAToken 
    ghost sumAllBalance() returns mathint {
        init_state axiom sumAllBalance() == 0;
    }

    hook Sstore balanceOf[KEY address a] uint256 balance (uint256 old_balance) STORAGE {
    havoc sumAllBalance assuming sumAllBalance@new() == sumAllBalance@old() + balance - old_balance;
    }

///////////////// Properties ///////////////////////

    /**
    * @title Rewards claiming when sufficient rewards exist
    * Ensures rewards are updated correctly after claiming, when there are enough
    * reward funds.
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
    */
    rule rewardsConsistencyWhenInsufficientRewards() {
        // Assuming single reward
        single_RewardToken_setup();

        env e;
        require e.msg.sender != currentContract;  // Cannot claim to contract
        require e.msg.sender != _TransferStrategy;

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
        
    /// @title The amount of rewards that was actually received by claimRewards() cannot exceed the initial amount of rewards
    rule getClaimableRewardsBefore_leq_claimed_claimRewardsOnBehalf()
    {
        env e;
        address onBehalfOf;
        address receiver;
        require receiver != currentContract;
        
        mathint balanceBefore = _DummyERC20_rewardToken.balanceOf(receiver);
        mathint claimableRewardsBefore = getClaimableRewards(e, onBehalfOf, _DummyERC20_rewardToken);
        claimSingleRewardOnBehalf(e, onBehalfOf, receiver, _DummyERC20_rewardToken);
        mathint balanceAfter = _DummyERC20_rewardToken.balanceOf(receiver);
        mathint deltaBalance = balanceAfter - balanceBefore;

        assert deltaBalance <= claimableRewardsBefore;
    }
