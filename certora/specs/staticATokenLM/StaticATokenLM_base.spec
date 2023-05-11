import "../methods/methods_base.spec"

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

    /// @title correct accrued value is fetched
    /// @notice assume a single asset
    invariant singleAssetAccruedRewards(env e0, address asset, address reward, address user)
        ((_RewardsController.getAssetListLength() == 1 && _RewardsController.getAssetByIndex(0) == asset)
            => (_RewardsController.getUserAccruedReward(asset, reward, user) == _RewardsController.getUserAccruedRewards(reward, user)))
        filtered { f -> !harnessOnlyMethods(f) }
            {
                preserved with (env e1){
                    setup(e1, user);
                    require asset != _RewardsController;
                    require asset != _TransferStrategy;
                    require reward != _StaticATokenLM;
                    require reward != _AToken;
                    require reward != _TransferStrategy;
                }
            }
