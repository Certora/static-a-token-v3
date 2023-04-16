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
        f -> (!harnessOnlyMethods(f) &&
            f.selector != initialize(address, string, string).selector) &&
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

    //fail. todo: check if property should hold
    //https://vaas-stg.certora.com/output/99352/5521be2ec21640feb23be9d8b1faa08a/?anonymousKey=e2a56ad93292b812fb66afa29a0ae8fcf53b4f37
    //https://vaas-stg.certora.com/output/99352/c288ca4de50e4f7ab76bfa70fac1c7ff/?anonymousKey=9cf2d1fb28a3b4f47b952eae91f3d330ea346181
    // invariant solvency_user_balance_leq_total_asset_CASE_SPLIT_redeem_in_shares_4(address user)
    //     balanceOf(user) <= _AToken.scaledBalanceOf(currentContract)
    //     filtered { f -> f.selector == redeem(uint256,address,address,bool).selector}
    //     {
    //         preserved redeem(uint256 shares, address receiver, address owner, bool toUnderlying) with (env e1) {
    //             requireInvariant solvency_total_asset_geq_total_supply();
    //             require balanceOf(owner) <= totalSupply(); //todo: replace with requireInvariant
    //             require receiver != _AToken;
    //             require user != _SymbolicLendingPool; // TODO: review !!!
    //         }
    //     }


    //pass -t=1400,-mediumTimeout=800,-depth=10 
    /// @notice Total supply is non-zero  only if total assets is non-zero
    invariant solvency_positive_total_supply_only_if_positive_asset()
        ((_AToken.scaledBalanceOf(currentContract) == 0) => (totalSupply() == 0))
        filtered { f -> f.selector != metaWithdraw(address,address,uint256,uint256,bool,uint256,(uint8,bytes32,bytes32)).selector 
                        && !harnessOnlyMethods(f) }
        {
            preserved redeem(uint256 shares, address receiver, address owner, bool toUnderlying) with (env e1) {
                requireInvariant solvency_total_asset_geq_total_supply();
                require balanceOf(owner) <= totalSupply(); //todo: replace with requireInvariant
            }
            preserved redeem(uint256 shares, address receiver, address owner) with (env e2) {
                requireInvariant solvency_total_asset_geq_total_supply();
                require balanceOf(owner) <= totalSupply(); 
            }
            preserved withdraw(uint256 assets, address receiver, address owner)  with (env e3) {
                requireInvariant solvency_total_asset_geq_total_supply();
                require balanceOf(owner) <= totalSupply(); 
            }

        }



    //fail on deposit if e1.msg.sender == currentContract
    //https://vaas-stg.certora.com/output/99352/83c1362989b540658dd72714c68f4f6a/?anonymousKey=00b5efbeb76fc09cbb12b5c0a53248703a16f5fe
    //https://vaas-stg.certora.com/output/99352/a929ada034a5437ca001dd11b221038b/?anonymousKey=a90c16f056686fdd38110f16f6ec8f72a8d2062b

    //pass with -t=1400,-mediumTimeout=800,-depth=15
    //https://vaas-stg.certora.com/output/99352/7252b6b75144419c825fb00f1f11acc8/?anonymousKey=8cb67238d3cb2a14c8fbad5c1c8554b00221de95
    //pass with -t=1400,-mediumTimeout=800,-depth=10

    /// @nitce Total asseta is greater than or equal to total supply.
    invariant solvency_total_asset_geq_total_supply()
        (_AToken.scaledBalanceOf(currentContract) >= totalSupply())
        filtered { f -> f.selector != metaWithdraw(address,address,uint256,uint256,bool,uint256,(uint8,bytes32,bytes32)).selector
                        && f.selector != redeem(uint256,address,address).selector
                        && f.selector != redeem(uint256,address,address,bool).selector
                        && !harnessOnlyMethods(f) }
        {
            preserved withdraw(uint256 assets, address receiver, address owner)  with (env e3) {
                require balanceOf(owner) <= totalSupply(); 
            }
            preserved deposit(uint256 assets, address receiver) with (env e4) {
                require balanceOf(receiver) <= totalSupply(); //todo: replace with requireInvariant
                require e4.msg.sender != currentContract; //todo: review
    }
            preserved deposit(uint256 assets, address receiver,uint16 referralCode, bool fromUnderlying) with (env e5) {
                require balanceOf(receiver) <= totalSupply(); //todo: replace with requireInvariant
                require e5.msg.sender != currentContract; //todo: review
            }
            preserved mint(uint256 shares, address receiver) with (env e6) {
                require balanceOf(receiver) <= totalSupply(); //todo: replace with requireInvariant
                require e6.msg.sender != currentContract; //todo: review
            }
            
        }

    //timeout
    //https://vaas-stg.certora.com/output/99352/cf6f23d546ed4834ae27bc4de2df81d7/?anonymousKey=a0ab74898224e42db0ef4770909848880d61abaa
    //timeout with  -t=1200,-mediumTimeout=800,-depth=10
    invariant solvency_total_asset_geq_total_supply_CASE_SPLIT_redeem()
        (_AToken.scaledBalanceOf(currentContract) >= totalSupply())
        filtered { f -> f.selector == redeem(uint256,address,address).selector}
        {
            preserved redeem(uint256 shares, address receiver, address owner) with (env e2) {
                require balanceOf(owner) <= totalSupply(); 
            }
        }
        
    //pass
    /// @title correct accrued value is fetched
    /// @notice assume a single asset
    //pass with rule_sanity basic except metaDeposit()
    //https://vaas-stg.certora.com/output/99352/ab6c92a9f96d4327b52da331d634d3ab/?anonymousKey=abb27f614a8656e6e300ce21c517009cbe0c4d3a
    //https://vaas-stg.certora.com/output/99352/d8c9a8bbea114d5caad43683b06d8ba0/?anonymousKey=a079d7f7dd44c47c05c866808c32235d56bca8e8
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



    //pass with --rule_sanity basic
    //https://vaas-stg.certora.com/output/99352/4df615c845e2445b8657ece2db477ce5/?anonymousKey=76379915d60fc1056ed4e5b391c69cd5bba3cce0
    /// @title Claiming rewards should not affect totalAssets() 
    rule totalAssets_stable(method f)
        filtered { f -> claimFunctions(f) }
    {
        env e;
        calldataarg args;
        mathint totalAssetBefore = totalAssets();
        f(e, args); 
        mathint totalAssetAfter = totalAssets();
        assert totalAssetAfter == totalAssetBefore;
    }

    //fail
    //https://vaas-stg.certora.com/output/99352/2104ed63c44845c2a8a793007224cb2a/?anonymousKey=f2e12ee6154f8b707b21fb62d1cc12a46a6c03b1
    rule totalAssets_stable_after_collectAndUpdateRewards()
    {
        env e;
        address reward;
        mathint totalAssetBefore = totalAssets();
        collectAndUpdateRewards(e, reward); 
        mathint totalAssetAfter = totalAssets();
        assert totalAssetAfter == totalAssetBefore;
    }


    //pass
    //https://vaas-stg.certora.com/output/99352/7d2ce2bb69ad4d71b4a179daa08633e4/?anonymousKey=7446e8a015ea9aa79cbc542c10b932e04169a0ab
    /// @title Receiving ATokens does not affect the amount of rewards fetched by collectAndUpdateRewards()
    rule reward_balance_stable_after_collectAndUpdateRewards()
    {
        uint256 totalAccrued = _RewardsController.getUserAccruedRewards(_AToken, currentContract);
        require (totalAccrued == 0);

        env e;
        address reward;

        mathint totalAssetBefore = totalAssets();
        
        collectAndUpdateRewards(e, reward); 
        mathint totalAssetAfter = totalAssets();

        assert totalAssetAfter == totalAssetBefore;
    }

    // //timeout
    // /// @title getTotalClaimableRewards() is stable unless rewards were claimed
    // rule totalClaimableRewards_stable(method f)
    //     filtered { f -> !f.isView && !claimFunctions(f)  && f.selector != initialize(address,string,string).selector  }
    // {
    //     env e;
    //     require e.msg.sender != currentContract;
    //     setup(e, 0);
    //     calldataarg args;
    //     address reward;
    //     require e.msg.sender != reward;
    //     require currentContract != e.msg.sender;
    //     require _AToken != e.msg.sender;
    //     require _RewardsController != e.msg.sender;
    //     require _DummyERC20_aTokenUnderlying  != e.msg.sender;
    //     require _DummyERC20_rewardToken != e.msg.sender;
    //     require _SymbolicLendingPool != e.msg.sender;
    //     require _TransferStrategy != e.msg.sender;
        
    //     require currentContract != reward;
    //     require _AToken != reward;
    //     require _RewardsController !=  reward;
    //     require _DummyERC20_aTokenUnderlying  != reward;
    //     require _SymbolicLendingPool != reward;
    //     require _TransferStrategy != reward;
    //     require _TransferStrategy != reward;


    //     mathint totalClaimableRewardsBefore = getTotalClaimableRewards(e, reward);
    //     f(e, args); 
    //     mathint totalClaimableRewardsAfter = getTotalClaimableRewards(e, reward);
    //     assert totalClaimableRewardsAfter == totalClaimableRewardsBefore;
    // }

    //pass with -t=1400,-mediumTimeout=800,-depth=10
    rule totalClaimableRewards_stable_CASE_SPLIT(method f)
    filtered { f -> !f.isView && !claimFunctions(f)
                        && f.selector != initialize(address,string,string).selector 
                        && f.selector != redeem(uint256,address,address,bool).selector 
                        && f.selector != redeem(uint256,address,address).selector 
                        && f.selector != withdraw(uint256,address,address).selector 
                        && f.selector != deposit(uint256,address).selector 
                        && f.selector != mint(uint256,address).selector 
                        && f.selector != metaWithdraw(address,address,uint256,uint256,bool,uint256,(uint8,bytes32,bytes32)).selector 
                        && f.selector !=claimSingleRewardOnBehalf(address,address,address).selector 
                        }
    {
        require _RewardsController.getAssetByIndex(0) != _RewardsController;
        require _RewardsController.getAssetListLength() > 0;
        
        uint256 totalAccrued = _RewardsController.getUserAccruedRewards(_AToken, currentContract);
        require (totalAccrued == 0);



        env e;
        address reward;

        mathint totalAssetBefore = totalAssets();
        
        collectAndUpdateRewards(e, reward); 
        mathint totalAssetAfter = totalAssets();

        assert totalAssetAfter == totalAssetBefore;
    }


    //timeout  -t=1400,-mediumTimeout=800,-depth=10 =10
    //pass with -t=1200,-mediumTimeout=1200,-depth=10 
    // 16 minutes
    //https://vaas-stg.certora.com/output/99352/12829795cff241098f304ce49f73051e/?anonymousKey=739f53463e398ed7d5b2eec101f254b6095e0841
    // 40 minutes
    //https://vaas-stg.certora.com/output/99352/5a29622bc18c438ba016a27162a82c84/?anonymousKey=130051cfba518c2cdf7f0e86ecc71ea05d98367b
    rule totalClaimableRewards_stable_CASE_SPLIT_redeem()
    {
        env e;
        require e.msg.sender != currentContract;
        setup(e, 0);
        address reward;
        require e.msg.sender != reward;
        require currentContract != e.msg.sender;
        require _AToken != e.msg.sender;
        require _RewardsController != e.msg.sender;
        require _DummyERC20_aTokenUnderlying  != e.msg.sender;
        require _DummyERC20_rewardToken != e.msg.sender;
        require _SymbolicLendingPool != e.msg.sender;
        require _TransferStrategy != e.msg.sender;
        
        require currentContract != reward;
        require _AToken != reward;
        require _RewardsController !=  reward;
        require _DummyERC20_aTokenUnderlying  != reward;
        require _SymbolicLendingPool != reward;
        require _TransferStrategy != reward;
        require _TransferStrategy != reward;

    //todo: run with different settings
        mathint totalClaimableRewardsBefore = getTotalClaimableRewards(e, reward);
        uint256 shares;
        address receiver;
        address owner;
        redeem(e, shares, receiver, owner); 
        mathint totalClaimableRewardsAfter = getTotalClaimableRewards(e, reward);
        assert totalClaimableRewardsAfter == totalClaimableRewardsBefore;
    }

    //timeout with -t=1000,-mediumTimeout=100,-depth=10 
    //timeout no SMT run:  -t=1200,-mediumTimeout=1000,-depth=6   -t=1200,-mediumTimeout=1200,-depth=10 
    rule totalClaimableRewards_stable_CASE_SPLIT_deposit()
    {
        env e;
        require e.msg.sender != currentContract;
        setup(e, 0);
        address reward;
        require e.msg.sender != reward;
        require currentContract != e.msg.sender;
        require _AToken != e.msg.sender;
        require _RewardsController != e.msg.sender;
        require _DummyERC20_aTokenUnderlying  != e.msg.sender;
        require _DummyERC20_rewardToken != e.msg.sender;
        require _SymbolicLendingPool != e.msg.sender;
        require _TransferStrategy != e.msg.sender;
        
        require currentContract != reward;
        require _AToken != reward;
        require _RewardsController !=  reward;
        require _DummyERC20_aTokenUnderlying  != reward;
        require _SymbolicLendingPool != reward;
        require _TransferStrategy != reward;
        require _TransferStrategy != reward;


        mathint totalClaimableRewardsBefore = getTotalClaimableRewards(e, reward);
        uint256 assets;
        address receiver;
        deposit(e, assets, receiver);
        mathint totalClaimableRewardsAfter = getTotalClaimableRewards(e, reward);
        assert totalClaimableRewardsAfter == totalClaimableRewardsBefore;
    }

    // //timeout
    // rule totalClaimableRewards_stable_less_requires_6(method f)
    //     filtered { f -> !f.isView && !claimFunctions(f)  && f.selector != initialize(address,string,string).selector  }
    // {
    //     env e;
    //     require e.msg.sender != currentContract;
    //     setup(e, 0);
    //     calldataarg args;
    //     address reward;
    //     require _DummyERC20_aTokenUnderlying != reward;
    //     require e.msg.sender != reward;
    //     require currentContract != e.msg.sender;
    //      require _RewardsController != e.msg.sender;
        
    //     require currentContract != reward;
    //     require _DummyERC20_aTokenUnderlying  != reward;
        

    //     mathint totalClaimableRewardsBefore = getTotalClaimableRewards(e, reward);
    //     f(e, args); 
    //     mathint totalClaimableRewardsAfter = getTotalClaimableRewards(e, reward);
    //     assert totalClaimableRewardsAfter == totalClaimableRewardsBefore;
    // }

    // //pass with -t=1400,-mediumTimeout=800,-depth=10
    // //https://vaas-stg.certora.com/output/99352/34ccc167c8d84d1985e3b0f75a5d41a6/?anonymousKey=e6f31abf1c7bb0cb66702a218b84b2830fde8928
    // rule totalClaimableRewards_stable_less_requires_7(method f)
    //     filtered { f -> !f.isView && !claimFunctions(f)
    //                     && f.selector != initialize(address,string,string).selector 
    //                     && f.selector != redeem(uint256,address,address,bool).selector 
    //                     && f.selector != redeem(uint256,address,address).selector 
    //                     && f.selector != withdraw(uint256,address,address).selector 
    //                     && f.selector != deposit(uint256,address).selector 
    //                     && f.selector != mint(uint256,address).selector 
    //                     && f.selector != metaWithdraw(address,address,uint256,uint256,bool,uint256,(uint8,bytes32,bytes32)).selector 
    //                     && f.selector !=claimSingleRewardOnBehalf(address,address,address).selector 
    //                     }
    // {
    //     env e;
    //     require e.msg.sender != currentContract;
    //     setup(e, 0);
    //     calldataarg args;
    //     address reward;
    //     require _DummyERC20_aTokenUnderlying != reward;
    //     require _AToken != reward;
    //     require e.msg.sender != reward;
    //     require _AToken != e.msg.sender;
    //     require _RewardsController != e.msg.sender;
        
    //     require currentContract != reward;
        
    //     mathint totalClaimableRewardsBefore = getTotalClaimableRewards(e, reward);
    //     f(e, args); 
    //     mathint totalClaimableRewardsAfter = getTotalClaimableRewards(e, reward);
    //     assert totalClaimableRewardsAfter == totalClaimableRewardsBefore;
    // }


    // //timeout
    // //https://vaas-stg.certora.com/output/99352/e755cdb34d84406ab17a782c4ffd6954/?anonymousKey=2efcab1e1dd4ea504c315b148b42ef3cec8acaa7
    // rule totalClaimableRewards_stable_less_requires_7_CASE_SPLIT_redeem()
    // {
    //     env e;
    //     require e.msg.sender != currentContract;
    //     setup(e, 0);
    //     address reward;
    //     require _DummyERC20_aTokenUnderlying != reward;
    //     require _AToken != reward;
    //     require e.msg.sender != reward;
    //     require _AToken != e.msg.sender;
    //     require _RewardsController != e.msg.sender;
        
    //     require currentContract != reward;
        
    //     mathint totalClaimableRewardsBefore = getTotalClaimableRewards(e, reward);
    //     uint256 shares;
    //     address receiver;
    //     address owner;
    //     redeem(e, shares, receiver, owner); 
    //     mathint totalClaimableRewardsAfter = getTotalClaimableRewards(e, reward);
    //     assert totalClaimableRewardsAfter == totalClaimableRewardsBefore;
    // }


    // //timeout
    // //https://vaas-stg.certora.com/output/99352/bee8d3a583c549e195c0f755bb804b34/?anonymousKey=4b9e6f6791ede0049659d54a07db5e0f146b4a42
    // rule totalClaimableRewards_stable_less_requires_7_CASE_SPLIT_deposit()
    // {
    //     env e;
    //     require e.msg.sender != currentContract;
    //     setup(e, 0);
    //     address reward;
    //     require _DummyERC20_aTokenUnderlying != reward;
    //     require _AToken != reward;
    //     require e.msg.sender != reward;
    //     require _AToken != e.msg.sender;
    //     require _RewardsController != e.msg.sender;
        
    //     require currentContract != reward;
        
    //     mathint totalClaimableRewardsBefore = getTotalClaimableRewards(e, reward);
    //     uint256 assets;
    //     address receiver;
    //     deposit(e, assets, receiver);
    //     mathint totalClaimableRewardsAfter = getTotalClaimableRewards(e, reward);
    //     assert totalClaimableRewardsAfter == totalClaimableRewardsBefore;
    // }


    //todo: add separate rules for redeem, mint
    //pass with rule_sanity basic, except metaDeposit, timeout withdraw(uint256,address,address)
    //https://vaas-stg.certora.com/output/99352/ee42e7f2603740de96a8a0aaf7c676ff/?anonymousKey=f7aaa1b8ed030a8f600136ec0b94ae0bc81a0e0c
    //pass
    //https://vaas-stg.certora.com/output/99352/109a4a815a9a4c3abcee760bf77c5f7d/?anonymousKey=f215580ed8e698028fdedecf096752c7a3e9363c
    //timeout

    /// @notice At a given block, getClaimableRewards() is unchanged unless rewards were claimed.
    // rule getClaimableRewards_stable(method f)
    //     filtered { f -> !f.isView
    //                     && !claimFunctions(f)
    //                     && f.selector != initialize(address,string,string).selector
    //                     && f.selector != deposit(uint256,address,uint16,bool).selector
    //                     && f.selector != redeem(uint256,address,address).selector
    //                     && f.selector != redeem(uint256,address,address,bool).selector
    //                     && f.selector != mint(uint256,address).selector
    //                     && f.selector != metaWithdraw(address,address,uint256,uint256,bool,uint256,(uint8,bytes32,bytes32)).selector
    //                     && f.selector !=claimSingleRewardOnBehalf(address,address,address).selector 
    //     }
    // {
    //     env e;
    //     calldataarg args;
    //     address user;
    //     address reward;
    
    //     require user != 0;

    //     require currentContract != user;
    //     require _AToken != user;
    //     require _RewardsController !=  user;
    //     require _DummyERC20_aTokenUnderlying  != user;
    //     require _DummyERC20_rewardToken != user;
    //     require _SymbolicLendingPool != user;
    //     require _TransferStrategy != user;
        
    //     require currentContract != reward;
    //     require _AToken != reward;
    //     require _RewardsController !=  reward; //
    //     require _DummyERC20_aTokenUnderlying  != reward;
    //     require _SymbolicLendingPool != reward; 
    //     require _TransferStrategy != reward;
        
    //     //require isRegisteredRewardToken(reward); //todo: review the assumption
    
    //     mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);

    //     require getRewardTokensLength() > 0;
    //     require getRewardToken(0) == reward; //todo: review
    //     require _RewardsController.getAvailableRewardsCount(_AToken)  > 0; //todo: review
    //     require _RewardsController.getRewardsByAsset(_AToken, 0) == reward; //todo: review
    //     f(e, args); 
    //     mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    //     assert claimableRewardsAfter == claimableRewardsBefore;
    // }
    // //timeout
    // //should pass after excluding claimSingleRewardOnBehalf
    // rule getClaimableRewards_stable_6(method f)
    //     filtered { f -> !f.isView
    //                     && !claimFunctions(f)
    //                     && f.selector != initialize(address,string,string).selector
    //                     && f.selector != deposit(uint256,address,uint16,bool).selector
    //                     && f.selector != redeem(uint256,address,address).selector
    //                     && f.selector != redeem(uint256,address,address,bool).selector
    //                     && f.selector != mint(uint256,address).selector
    //                     && f.selector != metaWithdraw(address,address,uint256,uint256,bool,uint256,(uint8,bytes32,bytes32)).selector
    //                     && f.selector !=claimSingleRewardOnBehalf(address,address,address).selector 
    //     }
    // {
    //     env e;
    //     calldataarg args;
    //     address user;
    //     address reward;
    
    //     require user != 0;

    
    //     mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);

    //     require getRewardTokensLength() > 0;
    //     require getRewardToken(0) == reward; //todo: review
    //     require _RewardsController.getAvailableRewardsCount(_AToken)  > 0; //todo: review
    //     require _RewardsController.getRewardsByAsset(_AToken, 0) == reward; //todo: review
    //     f(e, args); 
    //     mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    //     assert claimableRewardsAfter == claimableRewardsBefore;
    // }

    //pass with -t=1400,-mediumTimeout=800,-depth=15
    //https://vaas-stg.certora.com/output/99352/a10c05634b4342d6b31f777826444616/?anonymousKey=67bb71ebd716ef5d10be8743ded7b466f699e32c
    //pass with -t=1400,-mediumTimeout=800,-depth=10 
    rule getClaimableRewards_stable(method f)
        filtered { f -> !f.isView
                        && !claimFunctions(f)
                        && f.selector != initialize(address,string,string).selector
                        && f.selector != deposit(uint256,address,uint16,bool).selector
                        && f.selector != redeem(uint256,address,address).selector
                        && f.selector != redeem(uint256,address,address,bool).selector
                        && f.selector != mint(uint256,address).selector
                        && f.selector != metaWithdraw(address,address,uint256,uint256,bool,uint256,(uint8,bytes32,bytes32)).selector
                        && f.selector !=claimSingleRewardOnBehalf(address,address,address).selector 
                        && !harnessOnlyMethods(f)
        }
    {
        env e;
        calldataarg args;
        address user;
        address reward;
    
        require user != 0;

        require currentContract != reward;
        require _AToken != reward;
        require _RewardsController !=  reward; //
        require _DummyERC20_aTokenUnderlying  != reward;
        require _SymbolicLendingPool != reward; 
        require _TransferStrategy != reward;
        
        //require isRegisteredRewardToken(reward); //todo: review the assumption
    
        mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);

        require getRewardTokensLength() > 0;
        require getRewardToken(0) == reward; //todo: review
        require _RewardsController.getAvailableRewardsCount(_AToken)  > 0; //todo: review
        require _RewardsController.getRewardsByAsset(_AToken, 0) == reward; //todo: review
        f(e, args); 
        mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
        assert claimableRewardsAfter == claimableRewardsBefore;
    }

    //pass with -t=1400,-mediumTimeout=800,-depth=10 
    rule getClaimableRewards_stable_after_redeem()
    {
        env e;
        address user;
        address reward;
    
        require user != 0;

        require currentContract != reward;
        require _AToken != reward;
        require _RewardsController !=  reward; //
        require _DummyERC20_aTokenUnderlying  != reward;
        require _SymbolicLendingPool != reward; 
        require _TransferStrategy != reward;
        
        //require isRegisteredRewardToken(reward); //todo: review the assumption
    
        mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);

        require getRewardTokensLength() > 0;
        require getRewardToken(0) == reward; //todo: review
        require _RewardsController.getAvailableRewardsCount(_AToken)  > 0; //todo: review
        require _RewardsController.getRewardsByAsset(_AToken, 0) == reward; //todo: review
        uint256 shares;
        address receiver;
        address owner;
        bool toUnderlying;
        
        redeem(e, shares, receiver, owner, toUnderlying);

        mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
        assert claimableRewardsAfter == claimableRewardsBefore;
    }


    //pass
    rule getClaimableRewards_stable_after_deposit()
    {
        env e;
        address user;
        address reward;
        
        uint256 assets;
        address recipient;
        uint16 referralCode;
        bool fromUnderlying;

        require user != 0;

        
        mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);
        require getRewardTokensLength() > 0;
        require getRewardToken(0) == reward; //todo: review

        require _RewardsController.getAvailableRewardsCount(_AToken)  > 0; //todo: review
        require _RewardsController.getRewardsByAsset(_AToken, 0) == reward; //todo: review
        deposit(e, assets, recipient,referralCode,fromUnderlying);
        mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
        assert claimableRewardsAfter == claimableRewardsBefore;
    }


    
    //todo: remove
    //pass with --loop_iter=2 --rule_sanity basic
    //https://vaas-stg.certora.com/output/99352/290a1108baa64316ac4f20b5501b4617/?anonymousKey=930379a90af5aa498ec3fed2110a08f5c096efb3
    /// @title getClaimableRewards() is stable unless rewards were claimed
    rule getClaimableRewards_stable_after_refreshRewardTokens()
    {
        env e;
        address user;
        address reward;

        mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);
        refreshRewardTokens(e);

        mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
        assert claimableRewardsAfter == claimableRewardsBefore;
    }


    /// @title The amount of rewards that was actually received by claimRewards() cannot exceed the initial amount of rewards
    rule getClaimableRewardsBefore_leq_claimed_claimRewardsOnBehalf(method f)
    {   
        env e;
        address onBehalfOf;
        address receiver; 
        
        mathint balanceBefore = _DummyERC20_rewardToken.balanceOf(receiver);
        mathint claimableRewardsBefore = getClaimableRewards(e, onBehalfOf, _DummyERC20_rewardToken);
        claimSingleRewardOnBehalf(e, onBehalfOf, receiver, _DummyERC20_rewardToken);
        mathint balanceAfter = _DummyERC20_rewardToken.balanceOf(receiver);
        mathint deltaBalance = balanceAfter - balanceBefore;
    
        assert deltaBalance <= claimableRewardsBefore;
    }

    //todo: check property, debug fail, extend rule to general asset
    //https://vaas-stg.certora.com/output/99352/f9182b0d025346ebb41d87fcf538ace8/?anonymousKey=ba0ce76e377e6ae22b638d8811ff51390654cfe8
    //
    invariant validIndexOnLastInteraction(address user)
        getRewardsIndexOnLastInteraction(user, _DummyERC20_rewardToken) <=
        _RewardsController.getRewardsIndex(_AToken, _DummyERC20_rewardToken) 
    filtered { f -> !harnessOnlyMethods(f) }

    invariant validIndexOnLastInteraction_CASE_SPLIT_redeem(address user)
        getRewardsIndexOnLastInteraction(user, _DummyERC20_rewardToken) <=
        _RewardsController.getRewardsIndex(_AToken, _DummyERC20_rewardToken) 
    filtered { f -> f.selector == redeem(uint256,address,address,bool).selector}